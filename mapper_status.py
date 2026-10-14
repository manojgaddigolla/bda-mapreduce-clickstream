import sys

def main():
    """
    Mapper for Job 2: HTTP Status Code Analysis
    Input: Raw CSV clickstream lines from sys.stdin
    Output: key-value pairs formatted as 'status_code\t1'
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Skip CSV header line
        if line.startswith("timestamp,user_id"):
            continue

        parts = line.split(",")
        if len(parts) >= 4:
            status_code = parts[3].strip()
            # Emit (status_code, 1)
            print(f"{status_code}\t1")

if __name__ == "__main__":
    main()
