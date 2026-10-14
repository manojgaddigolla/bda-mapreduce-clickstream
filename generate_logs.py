import csv
import random
from datetime import datetime, timedelta

def generate_clickstream_logs(filename="clickstream.csv", num_records=25000):
    """
    Generates synthetic batch clickstream web server logs.
    Simulates user traffic, page visits, and HTTP response codes.
    """
    urls = [
        "/home",
        "/products",
        "/products/electronics",
        "/products/fashion",
        "/cart",
        "/checkout",
        "/login",
        "/contact",
        "/about"
    ]

    # Realistic status code distribution: mostly 200 OK, some 404 Not Found, rare 500 Server Error
    status_codes = [200, 404, 500, 301]
    status_weights = [0.82, 0.10, 0.05, 0.03]

    users = [f"user_{i}" for i in range(1, 51)]  # 50 unique users

    start_time = datetime(2026, 10, 14, 0, 0, 0)

    print(f"Generating {num_records} clickstream records into '{filename}'...")

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "user_id", "url", "status_code", "response_time_ms"])

        current_time = start_time
        for _ in range(num_records):
            # Advance time by 1 to 5 seconds per request
            current_time += timedelta(seconds=random.randint(1, 5))
            
            user = random.choice(users)
            url = random.choice(urls)
            status = random.choices(status_codes, weights=status_weights)[0]
            response_time = random.randint(45, 650)  # Response time between 45ms and 650ms

            writer.writerow([
                current_time.strftime("%Y-%m-%d %H:%M:%S"),
                user,
                url,
                status,
                response_time
            ])

    print(f"Successfully created '{filename}' with {num_records} records.")

if __name__ == "__main__":
    generate_clickstream_logs()
