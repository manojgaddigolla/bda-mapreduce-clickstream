import sys

def main():
    """
    Mapper for Job 1: Page Visit Count
    Input: Raw CSV clickstream lines from sys.stdin
    Output: key-value pairs formatted as 'URL\t1'
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Skip CSV header line
        if line.startswith("timestamp,user_id"):
            continue

        parts = line.split(",")
        if len(parts) >= 3:
            url = parts[2].strip()
            # Emit (URL, 1)
            print(f"{url}\t1")

if __name__ == "__main__":
    main()
