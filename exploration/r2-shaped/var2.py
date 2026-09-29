"""Sweep wrapper for engine v2: params from env R2 (JSON). EXPLORATORY."""
import json, os
from shaped2 import make
setup, journey = make(**json.loads(os.environ.get("R2", "{}")))
