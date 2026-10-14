import sys

def main():
    """
    Reducer for Job 3: User Activity Analysis
    Input: Sorted key-value pairs 'user_id\t1' from sys.stdin
    Output: 'user_id\tTotal_Requests'
    """
    current_user = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        user_id, count = parts[0], parts[1]

        try:
            count = int(count)
        except ValueError:
            continue

        if current_user == user_id:
            current_count += count
        else:
            if current_user is not None:
                print(f"{current_user}\t{current_count}")
            current_user = user_id
            current_count = count

    if current_user is not None:
        print(f"{current_user}\t{current_count}")

if __name__ == "__main__":
    main()
