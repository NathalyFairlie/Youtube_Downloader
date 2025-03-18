import subprocess
import sys

# List of required libraries
required_libraries = ['tkinter', 'yt-dlp', 'audioclipextractor', 'lameenc']

# Function to check and install libraries
def install_libraries():
    for lib in required_libraries:
        try:
            __import__(lib)
            print(f'{lib} is already installed.')
        except ImportError:
            print(f'{lib} not found. Installing...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

# Install the libraries
install_libraries()