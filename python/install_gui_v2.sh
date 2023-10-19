#!/bin/bash

# Get the directory where the install script is located
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the location of Anaconda
CONDA_PATH=$(dirname $(dirname $(which conda)))

# Create a start_ieeg_recon.sh script in the install directory
cat > "$INSTALL_DIR/start_ieeg_recon.sh" <<END
#!/bin/zsh
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate ieeg_recon_m1
cd "$INSTALL_DIR"
python "$INSTALL_DIR"/ieeg_recon_gui.py
END

# Give execute permissions to the start_ieeg_recon.sh script
chmod +x "$INSTALL_DIR/start_ieeg_recon.sh"

# Create an AppleScript wrapper for the bash script
cat > "$INSTALL_DIR/start_ieeg_recon.applescript" <<END
do shell script "$INSTALL_DIR/start_ieeg_recon.sh"
END

# Save the AppleScript as an application
osascript -e "tell application \"Script Editor\" to save (open POSIX file \"$INSTALL_DIR/start_ieeg_recon.applescript\") as \"application\" in POSIX file \"/Applications/iEEG-recon.app\""

# Give the system some time to catch up
sleep 5

# Set the application icon
cp "$INSTALL_DIR/figures/applet.icns" "/Applications/iEEG-recon.app/Contents/Resources/"

# Sign the code
xattr -rc /Applications/iEEG-recon.app

codesign -s - --deep /Applications/iEEG-recon.app

