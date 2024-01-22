import os
import subprocess

def main():
    print("\n\n------------Loading VoxTool...------------\n\n")

    # Get the directory where this script is located
    install_dir = os.path.dirname(os.path.abspath(__file__))

    # Assuming Anaconda is installed and added to the system PATH
    # Find the location of Anaconda
    conda_path = subprocess.check_output("where conda", shell=True).decode().strip()
    conda_dir = os.path.dirname(os.path.dirname(conda_path))

    # Activate the voxtool virtual environment
    activate_script = os.path.join(conda_dir, "Scripts", "activate")
    vox_env = "vt"  # Name of your conda environment

    # Launch the Python script from the voxtool environment
    vox_tool_launch_script = os.path.join(install_dir, "..", "voxTool", "launch_pyloc.py")

    # Construct and run the command
    command = f'cmd /c "{activate_script} {vox_env} && python "{vox_tool_launch_script}"'
    subprocess.call(command, shell=True)

if __name__ == "__main__":
    main()
