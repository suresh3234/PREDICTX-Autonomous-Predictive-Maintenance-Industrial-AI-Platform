import sys
from pathlib import Path

# Programmatically add repository root and apps/api to sys.path
ROOT_PATH = Path(__file__).resolve().parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

API_PATH = ROOT_PATH / "apps" / "api"
if str(API_PATH) not in sys.path:
    sys.path.insert(0, str(API_PATH))
