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

## Installation

The project includes an **automatic installation script** that handles everything:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/home_server_status_display.git
   cd home_server_status_display
