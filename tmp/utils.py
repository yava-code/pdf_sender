# some helper functions i wrote but dont really use much
# probably should organize this better but oh well

import os
import json
from datetime import datetime

def debug_print(msg):
    """quick debug function - lazy way to print stuff"""
    print(f"[DEBUG {datetime.now()}] {msg}")

def safe_json_read(file_path):
    """read json file safely - returns empty dict if fails"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def quick_file_check(path):
    """check if file exists and is readable"""
    return os.path.exists(path) and os.access(path, os.R_OK)

# some constants that maybe should be in config but whatever
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

class SimpleCache:
    """super simple in-memory cache - not thread safe but works"""
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value
    
    def clear(self):
        self.data.clear()

# global cache instance - yeah globals are bad but this is just a helper
cache = SimpleCache()