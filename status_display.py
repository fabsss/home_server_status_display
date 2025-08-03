import time
import psutil
import docker
from datetime import timedelta
from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
from luma.core.render import canvas
from PIL import ImageFont
import random

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

YELLOW = (255, 0, 0)  # Pure yellow in RGB

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
        return "green"
    elif status == "exited" or status == "stopped":
        return "red"
    else:
        return YELLOW

def get_temp_color(temp):
    """Return color based on CPU temperature thresholds."""
    if temp < 60:
        return "green"
    elif temp < 70:
        return YELLOW
    else:
        return "red"

def get_usage_color(percent):
    """Return color based on usage thresholds (RAM, Swap, CPU)."""
    if percent <= 60:
        return "green"
    elif percent < 80:
        return YELLOW
    else:
        return "red"

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

def display_status():
    """Update the display with system status."""
    global animation_frame, shift_x, shift_y

    while True:
        update_shift()
        with canvas(display) as draw:
            # Add 5 pixels headroom to the top for all lines
            y_offset = 5 + shift_y
            x_offset = shift_x

            # Uptime
            draw.text((x_offset + 0, y_offset + 0), f"Uptime: {get_uptime()}", font=font_small, fill="white")

            # CPU Temperature
            temp_str = get_cpu_temperature()
            temp_val = float(temp_str.replace("°C", ""))
            temp_color = get_temp_color(temp_val)
            draw.text((x_offset + 0, y_offset + 20), "CPU Temp: ", font=font_small, fill="white")
            draw.text((x_offset + 80, y_offset + 20), f"{temp_str}", font=font_small, fill=temp_color)

            # CPU Usage
            cpu = psutil.cpu_percent()
            cpu_color = get_usage_color(cpu)
            draw.text((x_offset + 0, y_offset + 40), "CPU: ", font=font_small, fill="white")
            draw.text((x_offset + 40, y_offset + 40), f"{cpu}%", font=font_small, fill=cpu_color)

            # RAM and Swap Usage (combined line)
            ram = psutil.virtual_memory()
            swap = psutil.swap_memory()
            ram_color = get_usage_color(ram.percent)
            swap_color = get_usage_color(swap.percent)
            draw.text((x_offset + 0, y_offset + 60), "RAM: ", font=font_small, fill="white")
            draw.text((x_offset + 40, y_offset + 60), f"{ram.percent}%", font=font_small, fill=ram_color)
            draw.text((x_offset + 80, y_offset + 60), "/", font=font_small, fill="white")
            draw.text((x_offset + 87, y_offset + 60), f"{swap.percent}%", font=font_small, fill=swap_color)

            # Disk Usage
            disk = psutil.disk_usage("/")
            disk_color = get_usage_color(disk.percent)
            draw.text((x_offset + 0, y_offset + 80), "Disk: ", font=font_small, fill="white")
            draw.text((x_offset + 40, y_offset + 80), f"{disk.percent}%", font=font_small, fill=disk_color)

            # Docker Status - Home Assistant and Supervisor (1 line, color coded)
            ha_status = get_docker_status("homeassistant")
            supervisor_status = get_docker_status("hassio_supervisor")
            ha_color = get_status_color(ha_status)
            sup_color = get_status_color(supervisor_status)
            draw.text((x_offset + 0, y_offset + 95), "Container:", font=font_small, fill="white")
            draw.text((x_offset + 65, y_offset + 95), "Hass", font=font_small, fill=ha_color)
            draw.text((x_offset + 95, y_offset + 95), "/", font=font_small, fill="white")
            draw.text((x_offset + 100, y_offset + 95), "Sup", font=font_small, fill=sup_color)

            # Animation
            draw_animation(draw, x_offset + 110 + animation_frame, y_offset + 110)

        time.sleep(1)

if __name__ == "__main__":
    display_status()
