# debug helpers that i use during development
# not really needed in production but keeps them around just in case

import time
import functools

def timing_decorator(func):
    """measure function execution time - useful for debugging"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"DEBUG: {func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

def log_function_calls(func):
    """log when functions are called - probably too verbose for prod"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"DEBUG: calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# quick and dirty profiling
class SimpleProfiler:
    def __init__(self):
        self.calls = {}
    
    def track(self, name):
        if name not in self.calls:
            self.calls[name] = 0
        self.calls[name] += 1
    
    def report(self):
        print("=== Function Call Report ===")
        for name, count in self.calls.items():
            print(f"{name}: {count} calls")

# global profiler instance
profiler = SimpleProfiler()