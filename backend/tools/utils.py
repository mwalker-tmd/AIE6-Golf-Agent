import os

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

def debug_print(msg):
    if DEBUG:
        print(msg)
