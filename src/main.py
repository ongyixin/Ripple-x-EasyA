import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mods.cli_handlers import cli_handle

def main():
    cli_handle()

if __name__ == "__main__":
    main()