"""EXPLORATORY sweep harness: params from env R2 (JSON)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simple import make
setup, journey, P = make(**json.loads(os.environ.get("R2", "{}")))
