import subprocess
import sys

def install_packages(package_list):
    """
    Installs a list of Python packages using pip.
    """
    print("Starting package installation...")
    for package in package_list:
        try:
            print(f"Attempting to install {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            print("Please try to install it manually using: pip install " + package)
        except Exception as e:
            print(f"An unexpected error occurred while installing {package}: {e}")

if __name__ == "__main__":
    required_packages = [
        "selenium",
        "webdriver-manager"
    ]
    
    install_packages(required_packages)
    print("\nSetup script finished.")
    print("If you encounter errors related to 'tkinter', ensure you have a complete Python installation or install it via your system's package manager (e.g., 'sudo apt-get install python3-tk' on Debian/Ubuntu).")
    print("You can now run the brute force tool: python brute_force_tool_fixed.py")