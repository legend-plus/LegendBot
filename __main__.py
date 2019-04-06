import json
from legend import Legend
import logging

with open("config/config.json") as f:
    config = json.load(f)

logging.basicConfig(level=logging.CRITICAL)

legend = Legend(config)
