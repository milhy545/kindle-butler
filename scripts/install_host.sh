#!/bin/bash
set -euo pipefail

# install_host.sh - Installs Kindle Butler interactive auto-run rules

# Ensure sudo is authenticated or use askpass
if [ -z "${SUDO_ASKPASS:-}" ] && [ -x /usr/bin/ssh-askpass ]; then
    export SUDO_ASKPASS=/usr/bin/ssh-askpass
fi

# 1. Detect Kindle USB ID
KINDLE_ID=$(lsusb | grep -i "Amazon Kindle" | head -n 1 | awk '{print $6}') || true

if [ -z "$KINDLE_ID" ]; then
    echo "❌ Kindle not detected. Please connect your Kindle via USB and try again."
    exit 1
fi

VID="${KINDLE_ID%:*}"
PID="${KINDLE_ID#*:}"

echo "✅ Found Kindle with VID:$VID PID:$PID"

# 2. Create the Host Runner Script
HOST_RUNNER="$HOME/.local/bin/kindle-butler-host-run"
mkdir -p "$(dirname "$HOST_RUNNER")"

cat <<EOF > "$HOST_RUNNER"
#!/bin/bash
set -euo pipefail

# Host-side wrapper to detect mount and launch interactive terminal
# Give some time for mounting
sleep 5

# Find Kindle mount point using findmnt (more robust)
KINDLE_MOUNT=\$(findmnt -rn -S LABEL=Kindle -o TARGET || findmnt -rn -S LABEL=KINDLE -o TARGET || echo "")

if [ -n "\$KINDLE_MOUNT" ]; then
    export DISPLAY=:0
    # Try to find XAUTHORITY if not set
    export XAUTHORITY="\${XAUTHORITY:-\$HOME/.Xauthority}"
    
    # Check if we have the app in the workspace
    PROJECT_DIR="$HOME/Develop/kindle_butler"
    if [ -d "\$PROJECT_DIR" ]; then
        cd "\$PROJECT_DIR"
        # Use the absolute path to uv if possible
        UV_BIN=\$(which uv || echo "uv")
        konsole --hold -e "\$UV_BIN" run python -m app.main start
    else
        notify-send "Kindle Butler" "❌ Project directory not found at \$PROJECT_DIR"
    fi
else
    # Log failure for diagnostics
    echo "\$(date) - Kindle mount not found" >> "\$HOME/.kindle-butler-error.log"
fi
EOF

chmod +x "$HOST_RUNNER"

# 3. Generate udev rule
UDEV_RULE="/etc/udev/rules.d/99-kindle-butler.rules"
# We use a cleaner RUN command that avoids complex escaping
RULE_CONTENT="ACTION==\"add\", SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$VID\", ATTR{idProduct}==\"$PID\", RUN+=\"/usr/bin/sudo -u $USER $HOST_RUNNER\""

echo "📝 Generating udev rule..."
echo "$RULE_CONTENT" | sudo -A tee "$UDEV_RULE" > /dev/null

# 4. Reload udev
echo "🔄 Reloading udev rules..."
sudo -A udevadm control --reload-rules
sudo -A udevadm trigger

echo "✨ Installation complete! An interactive terminal will pop up when you plug in your Kindle."
