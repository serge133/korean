#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
import sys
import json 
from datetime import datetime

ENCODING = 'utf-8'

def main(filename: str):
    data = []
    with open(filename, 'r', encoding=ENCODING) as f:
        data = json.loads(f.read())

    
    for mnemonic in data:
        mnemonic['timestamp'] = datetime(year=2025, month=10, day=26).timestamp()

    # Remove .json from the name
    filename = filename[:-5] + "_fix.json"

    with open(filename, "w", encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # Use json.dump for better formatting

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./fix_import_json.py <filename>.json")
        sys.exit(1)

    filename = sys.argv[1]
    main(filename)