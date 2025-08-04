# Home Server Status Display

This project displays live system and Docker container status information on an **SSD1351 OLED display** connected to a Raspberry Pi.

It shows:
- System uptime
- CPU usage & temperature
- RAM & Swap usage
- Disk usage
- Docker container status for:
  - Home Assistant (`homeassistant`)
  - Supervisor (`hassio_supervisor`)
- Network ping to Google
- Small pixel-shift animation to prevent OLED burn-in
- Night mode (automatic brightness reduction during configured hours)
- Graceful **shutdown screen** when the Raspberry Pi is powering off

---

## Hardware Requirements

- Raspberry Pi (any model with SPI support)
- SSD1351 OLED display (SPI interface, 128×128 pixels)
- Connected according to the `luma.oled` SPI pin configuration

---

## Software Requirements

The script uses:
- Python 3
- `luma.oled` for display control
- `psutil` for system stats
- `docker` Python SDK
- `Pillow` for text rendering

---

## Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/home_server_status_display.git
   cd home_server_status_display
