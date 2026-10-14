import sys

def main():
    """
    Mapper for Job 3: User Activity Analysis
    Input: Raw CSV clickstream lines from sys.stdin
    Output: key-value pairs formatted as 'user_id\t1'
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Skip CSV header line
        if line.startswith("timestamp,user_id"):
            continue

        parts = line.split(",")
        if len(parts) >= 2:
            user_id = parts[1].strip()
            # Emit (user_id, 1)
            print(f"{user_id}\t1")

if __name__ == "__main__":
    main()
