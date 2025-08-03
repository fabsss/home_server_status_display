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
display = ssd1351(serial)

# Load fonts
font_large = ImageFont.truetype("arial.ttf", 16)
font_small = ImageFont.truetype("arial.ttf", 12)

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
            # Uptime
            draw.text((0, 0), f"Uptime: {get_uptime()}", font=font_small, fill="white")

            # CPU Temperature
            draw.text((0, 20), f"CPU Temp: {get_cpu_temperature()}", font=font_small, fill="white")

            # RAM Usage
            ram = psutil.virtual_memory()
            draw.text((0, 40), f"RAM: {ram.percent}%", font=font_small, fill="white")

            # CPU Usage
            cpu = psutil.cpu_percent()
            draw.text((0, 60), f"CPU: {cpu}%", font=font_small, fill="white")

            # Swap Usage
            swap = psutil.swap_memory()
            draw.text((0, 80), f"Swap: {swap.percent}%", font=font_small, fill="white")

            # Docker Status
            ha_status = get_docker_status("home-assistant")
            draw.text((0, 100), f"HA: {ha_status}", font=font_small, fill="white")

            # Animation
            draw_animation(draw, 110 + animation_frame, 110)

        time.sleep(1)

if __name__ == "__main__":
    display_status()
