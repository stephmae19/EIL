import subprocess
import os
import sys


def create_executable(script_path, one_file=True, no_console=False):
    """
    Wraps the PyInstaller command to convert a .py file to an executable.

    :param script_path: Path to your python script
    :param one_file: If True, bundles everything into a single .exe
    :param no_console: If True, hides the console window (useful for GUI apps)
    """
    if not os.path.exists(script_path):
        print(f"Error: The file {script_path} was not found.")
        return

    # Base command
    cmd = ["pyinstaller", script_path]

    # Add flags
    if one_file:
        cmd.append("--onefile")

    if no_console:
        cmd.append("--noconsole")

    print(f"Compiling {script_path}...")

    try:
        # Run the command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Success! Your executable is in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print("An error occurred during compilation.")
        print(e.stderr)


if __name__ == "__main__":
    # Change 'your_script.py' to your target file
    target_script = "your_script.py"

    # Set to True for a single file, False for a folder of dependencies
    bundle_as_one = True

    # Set to True if you want a GUI app (no black terminal window)
    hide_window = False

    create_executable(target_script, bundle_as_one, hide_window)