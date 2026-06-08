import os
import subprocess
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting Streamlit on port 5000")
    proc = subprocess.run(["uv", "run", "streamlit", "run", "app.py"])
    sys.exit(proc.returncode)
