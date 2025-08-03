import time
import psutil
import docker
from datetime import timedelta
from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
from luma.core.render import canvas
from PIL import ImageFont
import random
import subprocess

# Initialize Docker client
docker_client = docker.from_env()

# Initialize SPI interface and SSD1351 display
serial = spi(port=0, device=0)
display = ssd1351(serial, rotate=3)

# Load fonts
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_large = ImageFont.truetype(font_path, 16)
font_small = ImageFont.truetype(font_path, 12)

# Animation state
animation_frame = 0

# Add these global variables at the top of your script
shift_x = 0
shift_y = 0
shift_direction = 1
shift_counter = 0

# Because my SSD1351 diplay uses BGR color format I need to define colors in BGR
# These colors are defined in BGR format for compatibility with the SSD1351 display
# YELLOW is defined as pure yellow in RGB, which is (255, 255, 0) in BGR it is (0, 255, 255)
# RED is defined as pure red in RGB, which is (255, 0, 0) in BGR it is (0, 0, 255)
# GREEN is defined as pure green in RGB, which is (0, 255, 0) in BGR it is (0, 255, 0)  
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)

def get_uptime():
    """Get system uptime."""
    return str(timedelta(seconds=int(time.time() - psutil.boot_time())))

def get_cpu_temperature():
    """Get CPU temperature."""
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = int(f.read()) / 1000.0
    return f"{temp:.1f}°C"

def get_docker_status(container_name):
    """Get the status of a Docker container."""
    try:
        container = docker_client.containers.get(container_name)
        return container.status
    except docker.errors.NotFound:
        return "Not Found"

def get_status_color(status):
    """Return color based on container status."""
    if status == "running":
        return  GREEN
    elif status == "exited" or status == "stopped":
        return  RED
    else:
        return YELLOW

def get_temp_color(temp):
    """Return color based on CPU temperature thresholds."""
    if temp < 60:
        return GREEN
    elif temp < 70:
        return YELLOW
    else:
        return RED

def get_usage_color(percent):
    """Return color based on usage thresholds (RAM, Swap, CPU)."""
    if percent <= 60:
        return GREEN
    elif percent < 80:
        return YELLOW
    else:
        return RED

def draw_animation(draw, x, y):
    """Draw a small animation to indicate the script is running."""
    global animation_frame
    size = 5
    draw.rectangle((x, y, x + size, y + size), outline="white", fill="white")
    animation_frame = (animation_frame + 1) % 10

def update_shift():
    """Update the pixel shift offset to prevent OLED burn-in."""
    global shift_x, shift_y, shift_direction, shift_counter
    # Change shift every 60 cycles (~1 minute if sleep is 1s)
    shift_counter += 1
    if shift_counter >= 60:
        shift_counter = 0
        # Cycle through 4 directions: right, down, left, up
        if shift_direction == 1:
            shift_x += 2
            if shift_x > 4:
                shift_direction = 2
        elif shift_direction == 2:
            shift_y += 2
            if shift_y > 4:
                shift_direction = 3
        elif shift_direction == 3:
            shift_x -= 2
            if shift_x < -4:
                shift_direction = 4
        elif shift_direction == 4:
            shift_y -= 2
            if shift_y < -4:
                shift_direction = 1

def get_ping(host="www.google.com"):
    """Return ping time to host in ms, or 'timeout' if unreachable."""
    try:
        # Use the system ping command, send 1 packet, wait max 1 second
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        # Parse output for time=XX ms
        for line in output.splitlines():
            if "time=" in line:
                time_ms = line.split("time=")[-1].split(" ")[0]
                return f"{time_ms} ms"
        return "timeout"
    except Exception:
        return "timeout"

def display_status():
    """Update the display with system status."""
    global animation_frame, shift_x, shift_y

    while True:
        update_shift()
        with canvas(display) as draw:
            # Add 5 pixels headroom to the top for all lines
            y_offset = 5 + shift_y
            x_offset = shift_x

            # Helper for text width (Pillow >=10)
            def get_text_width(text, font):
                try:
                    bbox = font.getbbox(text)
                    return bbox[2] - bbox[0]
                except AttributeError:
                    return font.getsize(text)[0]

            # Uptime
            uptime_str = get_uptime()
            uptime_width = get_text_width(uptime_str, font_small)
            draw.text((x_offset + 0, y_offset + 0), "Uptime:", font=font_small, fill="white")
            draw.text((x_offset + display.width - uptime_width-1, y_offset + 0), uptime_str, font=font_small, fill="white")

            # CPU Usage + Temperature
            temp_str = get_cpu_temperature()
            temp_val = float(temp_str.replace("°C", ""))
            cpu = psutil.cpu_percent()
            cpu_color = get_usage_color(cpu)
            cpu_str = f"{cpu}%"
            cpu_width = get_text_width(cpu_str, font_small)
            temp_color = get_temp_color(temp_val)
            temp_width = get_text_width(temp_str, font_small)
            right_x = x_offset + display.width-1 # Needed for CPU and RAM lines
            slash_str = " / " # Needed for CPU and RAM lines
            slash_width = get_text_width(slash_str, font_small) # Needed for CPU and RAM lines

            draw.text((x_offset + 0, y_offset + 20), "CPU:", font=font_small, fill="white")
            #draw.text((x_offset + display.width - cpu_width-1, y_offset + 40), cpu_str, font=font_small, fill=cpu_color)

            #draw.text((x_offset + 0, y_offset + 20), "/", font=font_small, fill="white")
            #draw.text((x_offset + display.width - temp_width-1, y_offset + 20), temp_str, font=font_small, fill=temp_color)

            draw.text((right_x - cpu_width - slash_width - temp_width, y_offset + 20), cpu_str, font=font_small, fill=cpu_color)
            draw.text((right_x - slash_width - temp_width, y_offset + 20), slash_str, font=font_small, fill="white")
            draw.text((right_x - temp_width, y_offset + 20), temp_str, font=font_small, fill=temp_color)


            # RAM and Swap Usage (combined line, right aligned)
            ram = psutil.virtual_memory()
            swap = psutil.swap_memory()
            ram_color = get_usage_color(ram.percent)
            swap_color = get_usage_color(swap.percent)
            ram_swap_str = f"{ram.percent}% / {swap.percent}%"
            ram_swap_width = get_text_width(ram_swap_str, font_small)
            draw.text((x_offset + 0, y_offset + 40), "RAM:", font=font_small, fill="white")
            ram_str = f"{ram.percent}%"
            swap_str = f"{swap.percent}%"
            
            ram_width = get_text_width(ram_str, font_small)
            swap_width = get_text_width(swap_str, font_small)

            draw.text((right_x - ram_width - slash_width - swap_width, y_offset + 40), ram_str, font=font_small, fill=ram_color)
            draw.text((right_x - slash_width - swap_width, y_offset + 40), slash_str, font=font_small, fill="white")
            draw.text((right_x - swap_width, y_offset + 40), swap_str, font=font_small, fill=swap_color)

            # Disk Usage
            disk = psutil.disk_usage("/")
            disk_color = get_usage_color(disk.percent)
            disk_str = f"{disk.percent}%"
            disk_width = get_text_width(disk_str, font_small)
            draw.text((x_offset + 0, y_offset + 60), "Disk:", font=font_small, fill="white")
            draw.text((x_offset + display.width - disk_width-1, y_offset + 60), disk_str, font=font_small, fill=disk_color)

            # Docker Status - Home Assistant and Supervisor (right aligned)
            ha_status = get_docker_status("homeassistant")
            supervisor_status = get_docker_status("hassio_supervisor")
            ha_color = get_status_color(ha_status)
            sup_color = get_status_color(supervisor_status)
            draw.text((x_offset + 0, y_offset + 80), "Container:", font=font_small, fill="white")
            draw.text((x_offset + 65, y_offset + 80), "Hass", font=font_small, fill=ha_color)
            draw.text((x_offset + 95, y_offset + 80), "/", font=font_small, fill="white")
            draw.text((x_offset + 100, y_offset + 80), "Sup", font=font_small, fill=sup_color)

            # Animation
            draw_animation(draw, x_offset + 110 + animation_frame, y_offset + 110)

            # Ping to www.google.com (bottom line)
            ping_result = get_ping()
            draw.text((x_offset + 0, y_offset + 100), f"Ping: {ping_result}", font=font_small, fill="white")

        time.sleep(1)

if __name__ == "__main__":
    display_status()
