# Home Server Status Display

This project displays status information of your Raspberry Pi Home Server on an **SSD1351 OLED display**.  
The following information is shown:

- **System uptime**
- **CPU usage & temperature** (with color-coded warning levels)
- **RAM and swap usage**
- **Disk usage**
- **Docker container status** (e.g., Home Assistant, Supervisor)
- **Ping time to www.google.com**
- **Pixel shifting** to prevent OLED burn-in
- **Automatic night mode** with reduced brightness
- **Shutdown screen** when the system is powering off

The display is controlled via **SPI**.

---

## Hardware Requirements

- Raspberry Pi (tested with Raspberry Pi 4)
- OLED display **SSD1351** (128x128, SPI)
- Wiring (GPIO for SPI, Data/Command, Reset)

**Default wiring** (configurable in `status_display.py`):

| Signal         | GPIO Pin  |
|----------------|-----------|
| VCC            | 3.3V      |
| GND            | GND       |
| SCK (CLK)      | GPIO 11   |
| MOSI           | GPIO 10   |
| CS             | GPIO 8    |
| DC             | GPIO 24   |
| RST            | GPIO 25   |

---

## Configuration

*Night mode parameters can be changed at the top of status_display.py:

```
NIGHTMODE_START = 23   # Start hour (23 = 11 PM)
NIGHTMODE_END   = 6    # End hour (6 = 6 AM)
NIGHT_CONTRAST  = 50   # Brightness/contrast at night (0..255)
DAY_CONTRAST    = 200  # Brightness/contrast during the day (0..255)
```

---
## Installation

The project includes an **automatic installation script** that handles everything:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/home_server_status_display.git
   cd home_server_status_display
2. **Install via bash script**:
   ```bash
   chmod +x install.sh
   ./install.sh


**What the Script does:**
What the installation script does:
1. Enable SPI interface in /boot/config.txt and via raspi-config
2. Update system packages
3. Install required dependencies:
   - Python 3 + venv + dev headers
   - luma.oled dependencies
4. Create Python virtual environment and install Python dependencies:
   - psutil, docker, pillow, luma.oled
5. Create a systemd service to run the script automatically at boot
6. Enable & start the service
