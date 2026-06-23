$ErrorActionPreference = "Stop"
python -m nuitka --module license_guard/guard.py --output-dir=build/compiled
