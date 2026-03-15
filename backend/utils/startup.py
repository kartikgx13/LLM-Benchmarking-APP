import subprocess
import requests
import time
import shutil
import platform
from config import OLLAMA_URL

#function to check if ollama is installed
def ollama_installed():
    return shutil.which("ollama") is not None

#function to install ollama
def install_ollama():
    system = platform.system()

    if system == "Darwin" or system == "Linux":
        subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh",
            shell=True,
            check=True
        )
    elif system == "Windows":
        print("Please install Ollama manually from https://ollama.com/download")

    print("Ollama installation complete")

#function to check if ollama is running
def ollama_running():
    try:
        requests.get(OLLAMA_URL)
        return True
    except:
        return False

#function to start ollama if not running
def start_ollama():

    if not ollama_running():

        print("Starting Ollama server...")

        subprocess.Popen(["ollama", "serve"])

        # wait until Ollama responds
        for _ in range(10):
            if ollama_running():
                print("Ollama server started")
                return
            time.sleep(1)

        print("Warning: Ollama did not start properly")

#function to install ollama if not installed
def setup_ollama():
    if not ollama_installed():

        install_ollama()

    start_ollama()