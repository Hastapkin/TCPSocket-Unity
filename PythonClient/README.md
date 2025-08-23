# Unity TCP Camera Stream - Python Client

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Start the Unity scene with the `CameraStreamer` component running, then:

```bash
python client.py --host 127.0.0.1 --port 5001
```

Press ESC in the window to stop.

