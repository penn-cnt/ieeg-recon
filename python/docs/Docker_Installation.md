
# Docker Desktop Installation on Windows with Hyper-V

## Prerequisites
- **Windows Version**: Windows 10 64-bit (Professional, Enterprise, or Education).
- **Hardware Virtualization**: Must be supported and enabled in BIOS/UEFI settings.
- **Windows Features**: Hyper-V and Containers features need to be enabled.

## Installation Steps
### 1. Download Docker Desktop
- Visit [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-windows/) and download the Docker Desktop installer for Windows.

### 2. Run the Installer
- Execute the installer and follow the instructions.
- When prompted, choose **'Use Hyper-V'** over WSL 2.

### 3. Complete Installation
- Restart your computer if necessary after installation.

## Post-Installation Configuration
### 1. Open Docker Desktop
- Launch Docker Desktop from the Start menu.

### 2. Adjust Memory Settings
- Navigate to Settings in Docker Desktop.
- Go to the 'Resources' section, then the 'Advanced' tab.
- Move the memory slider to allocate **maximum available memory**.
- Click 'Apply & Restart'.

## Verifying Installation
- Open a command prompt or PowerShell.
- Check the Docker version with `docker --version`.
- Run `docker run hello-world` to confirm Docker can pull and run images.

## Notes
- Administrative privileges are required for installation and configuration.
- Allocating maximum memory might impact the performance of other applications.
- Keep Docker Desktop updated for the best experience.

## Additional Tips
- Refer to Docker documentation for more details and best practices.
- Consider Docker Compose for managing multi-container Docker applications.

# Docker Desktop Installation on Mac

## Prerequisites
- **macOS Version**: macOS must be version 10.14 or newer.
- **Chip Support**: Intel chip or Apple chip.
- **Virtualization**: Ensure hardware virtualization is enabled.

## Installation Steps
### 1. Download Docker Desktop for Mac
- Go to [Docker Hub](https://hub.docker.com/editions/community/docker-ce-desktop-mac/) and download the Docker Desktop installer for Mac.

### 2. Install Docker Desktop
- Open the `.dmg` file and drag the Docker icon to the Applications folder.
- Open Docker from the Applications folder.

### 3. Grant Permissions
- You might need to grant permissions for Docker to run. Follow any on-screen instructions.

## Post-Installation Configuration
- Docker Desktop does not require additional memory configuration as it automatically manages resources based on availability.

## Verifying Installation
- Open a terminal.
- Check Docker version with `docker --version`.
- Run `docker run hello-world` to test pulling and running images.

## Notes
- Docker Desktop will request your admin password during the installation process for setting permissions.
- Keep Docker Desktop updated for optimal performance and security.
- Module 3 using AntsPyNet will require at least 16Gb of memory, but the user is free to use any other atlas in MNI space if that much memory is not available
