import time
import psutil
import docker
from datetime import timedelta
from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
from luma.core.render import canvas
from PIL import ImageFont

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
        return "yellow"

def draw_animation(draw, x, y):
    """Draw a small animation to indicate the script is running."""
    global animation_frame
    size = 5
    draw.rectangle((x, y, x + size, y + size), outline="white", fill="white")
    animation_frame = (animation_frame + 1) % 10

def display_status():
    """Update the display with system status."""
    global animation_frame

    while True:
        with canvas(display) as draw:
            # Add 5 pixels headroom to the top for all lines
            y_offset = 5

            # Uptime
            draw.text((0, y_offset + 0), f"Uptime: {get_uptime()}", font=font_small, fill="white")

            # CPU Temperature
            draw.text((0, y_offset + 20), f"CPU Temp: {get_cpu_temperature()}", font=font_small, fill="white")

            # RAM and Swap Usage (combined line)
            ram = psutil.virtual_memory()
            swap = psutil.swap_memory()
            draw.text((0, y_offset + 40), f"RAM: {ram.percent}%  / {swap.percent}%", font=font_small, fill="white")

            # CPU Usage
            cpu = psutil.cpu_percent()
            draw.text((0, y_offset + 60), f"CPU: {cpu}%", font=font_small, fill="white")

            # Docker Status - Home Assistant and Supervisor (1 line, color coded)
            ha_status = get_docker_status("homeassistant")
            supervisor_status = get_docker_status("hassio_supervisor")
            ha_color = get_status_color(ha_status)
            sup_color = get_status_color(supervisor_status)
            # Show service name in color, status in white
            draw.text((0, y_offset + 80), "Container:", font=font_small, fill="white")
            draw.text((30, y_offset + 80), "Hass", font=font_small, fill=ha_color)
            draw.text((55, y_offset + 80), "/", font=font_small, fill="white")
            draw.text((60, y_offset + 80), "Sup", font=font_small, fill=sup_color)

            # Animation
            draw_animation(draw, 110 + animation_frame, y_offset + 110)

        time.sleep(1)

if __name__ == "__main__":
    display_status()
