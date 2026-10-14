import sys

def main():
    """
    Reducer for Job 1: Page Visit Count
    Input: Sorted key-value pairs 'URL\t1' from sys.stdin
    Output: 'URL\tTotal_Visits'
    """
    current_url = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        url, count = parts[0], parts[1]

        try:
            count = int(count)
        except ValueError:
            continue

        # In Hadoop MapReduce, input to reducer is sorted by key
        if current_url == url:
            current_count += count
        else:
            if current_url is not None:
                print(f"{current_url}\t{current_count}")
            current_url = url
            current_count = count

    # Emit the last key
    if current_url is not None:
        print(f"{current_url}\t{current_count}")

if __name__ == "__main__":
    main()
