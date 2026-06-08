import os
import subprocess
import sys

STREAMLIT_PORT = 5000

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Starting Streamlit on port {STREAMLIT_PORT}")
    proc = subprocess.run(
        [
            "uv", "run", "streamlit", "run", "app.py",
        ]
    )
    sys.exit(proc.returncode)
