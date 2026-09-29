"""Sweep wrapper: params from env R2 (JSON). EXPLORATORY."""
import json, os
from shaped import make
setup, journey = make(**json.loads(os.environ.get("R2", "{}")))
