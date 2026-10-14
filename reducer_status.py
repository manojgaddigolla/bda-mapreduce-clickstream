import sys

def main():
    """
    Reducer for Job 2: HTTP Status Code Analysis
    Input: Sorted key-value pairs 'status_code\t1' from sys.stdin
    Output: 'status_code\tTotal_Count'
    """
    current_status = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        status, count = parts[0], parts[1]

        try:
            count = int(count)
        except ValueError:
            continue

        if current_status == status:
            current_count += count
        else:
            if current_status is not None:
                print(f"{current_status}\t{current_count}")
            current_status = status
            current_count = count

    if current_status is not None:
        print(f"{current_status}\t{current_count}")

if __name__ == "__main__":
    main()
