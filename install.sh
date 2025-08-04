#!/bin/bash
set -e

SERVICE_NAME="status_display"
VENV_DIR="luma-env"
PYTHON_VERSION="python3"

echo "==============================="
echo " Home Server Status Display"
echo " Installation Script"
echo "==============================="

# 1. Enable SPI interface
echo "[1/6] Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi
sudo raspi-config nonint do_spi 0

# 2. Update system
echo "[2/6] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# 3. Install required system packages
echo "[3/6] Installing required system packages..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    build-essential \
    libopenjp2-7 \
    libtiff5 \
    git \
    docker.io \
    fonts-dejavu-core

# 4. Create Python virtual environment and install dependencies
echo "[4/6] Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_VERSION -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install psutil docker pillow luma.oled

deactivate

# 5. Create systemd service
echo "[5/6] Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Home Server Status Display
After=network.target

[Service]
Type=simple
ExecStart=$(pwd)/$VENV_DIR/bin/python $(pwd)/status_display.py
WorkingDirectory=$(pwd)
Restart=always
User=$USER
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

# 6. Enable and start service
echo "[6/6] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "==============================="
echo " Installation complete!"
echo " The display service is now running."
echo "==============================="
echo "To check status:   sudo systemctl status $SERVICE_NAME"
echo "To view logs:      journalctl -u $SERVICE_NAME -f"
