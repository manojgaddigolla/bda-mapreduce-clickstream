import os
import subprocess
import time
import matplotlib.pyplot as plt

OUTPUT_DIR = "output"
DATA_FILE  = "clickstream.csv"

# ── Helpers ──────────────────────────────────────────────────────────────────

def run_mapreduce_job(mapper_script, reducer_script, input_file, output_file, header_lines=None):
    """
    Standard Hadoop-Streaming MapReduce execution:
      Map Phase -> Shuffle & Sort -> Reduce Phase -> Write output

    header_lines: list of comment strings written at the top of the output file.
    """
    start = time.time()

    with open(input_file, "r", encoding="utf-8") as infile:
        map_proc = subprocess.Popen(
            ["python", mapper_script],
            stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        map_out, map_err = map_proc.communicate()

    if map_proc.returncode != 0:
        print(f"  [ERROR] Mapper failed ({mapper_script}): {map_err.strip()}")
        return None

    # Shuffle & Sort
    sorted_input = "\n".join(sorted(l for l in map_out.strip().split("\n") if l)) + "\n"

    red_proc = subprocess.Popen(
        ["python", reducer_script],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    red_out, red_err = red_proc.communicate(input=sorted_input)

    if red_proc.returncode != 0:
        print(f"  [ERROR] Reducer failed ({reducer_script}): {red_err.strip()}")
        return None

    with open(output_file, "w", encoding="utf-8") as f:
        # Write comment header block at the top of the output file
        if header_lines:
            for line in header_lines:
                f.write(f"# {line}\n")
            f.write("#" + "-" * 50 + "\n")
        f.write(red_out)

    elapsed = time.time() - start
    print(f"  [OK] {os.path.basename(output_file):<28}  ({elapsed:.3f}s)")
    return red_out


def generate_summary_chart():
    """Generates summary_chart.png from MapReduce output files."""
    pages, page_counts = [], []
    with open(os.path.join(OUTPUT_DIR, "output_pages.txt"), "r") as f:
        for line in f:
            p = line.strip().split("\t")
            if len(p) == 2:
                pages.append(p[0])
                page_counts.append(int(p[1]))

    statuses, status_counts = [], []
    with open(os.path.join(OUTPUT_DIR, "output_status.txt"), "r") as f:
        for line in f:
            p = line.strip().split("\t")
            if len(p) == 2:
                statuses.append(p[0])
                status_counts.append(int(p[1]))

    user_data = []
    with open(os.path.join(OUTPUT_DIR, "output_users.txt"), "r") as f:
        for line in f:
            p = line.strip().split("\t")
            if len(p) == 2:
                user_data.append((p[0], int(p[1])))
    user_data.sort(key=lambda x: x[1], reverse=True)
    top_users  = [x[0] for x in user_data[:10]]
    top_counts = [x[1] for x in user_data[:10]]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    plt.suptitle("Batch MapReduce Clickstream Analytics — Results Summary",
                 fontsize=14, fontweight="bold")

    axes[0].barh(pages, page_counts, color="#3498db")
    axes[0].set_title("Job 1: Page Visit Distribution")
    axes[0].set_xlabel("Total Visits")
    axes[0].invert_yaxis()

    colors = ["#2ecc71" if s == "200" else
              "#f39c12" if s == "301" else
              "#e67e22" if s == "404" else "#e74c3c"
              for s in statuses]
    axes[1].pie(status_counts, labels=[f"HTTP {s}" for s in statuses],
                autopct="%1.1f%%", colors=colors, startangle=140)
    axes[1].set_title("Job 2: HTTP Status Codes")

    axes[2].bar(top_users, top_counts, color="#9b59b6")
    axes[2].set_title("Job 3: Top 10 Active Users")
    axes[2].set_ylabel("Total Requests")
    axes[2].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig("summary_chart.png", dpi=200)
    plt.close()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Batch MapReduce Clickstream Log Analysis")
    print("=" * 55)
    print(f"  Input  : {DATA_FILE}")
    print(f"  Output : {OUTPUT_DIR}/")
    print("-" * 55)
    print(f"  {'Job':<35}  {'Time':>6}")
    print("-" * 55)

    if not os.path.exists(DATA_FILE):
        import generate_logs
        generate_logs.generate_clickstream_logs()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    run_mapreduce_job(
        "mapper_pages.py", "reducer_pages.py", DATA_FILE,
        os.path.join(OUTPUT_DIR, "output_pages.txt"),
        header_lines=[
            "Job 1 Output : Page Visit Count",
            f"Input File   : {DATA_FILE}",
            f"Generated    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "Mapper       : mapper_pages.py  (emits URL -> 1 for each log record)",
            "Reducer      : reducer_pages.py (sums total visits per URL)",
            "Format       : <URL> [TAB] <Total_Visit_Count>",
        ]
    )
    run_mapreduce_job(
        "mapper_status.py", "reducer_status.py", DATA_FILE,
        os.path.join(OUTPUT_DIR, "output_status.txt"),
        header_lines=[
            "Job 2 Output : HTTP Status Code Distribution",
            f"Input File   : {DATA_FILE}",
            f"Generated    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "Mapper       : mapper_status.py  (emits Status_Code -> 1 for each log record)",
            "Reducer      : reducer_status.py (sums total count per HTTP status code)",
            "Format       : <HTTP_Status_Code> [TAB] <Total_Count>",
            "Status Codes : 200=OK, 301=Redirect, 404=Not Found, 500=Server Error",
        ]
    )
    run_mapreduce_job(
        "mapper_users.py", "reducer_users.py", DATA_FILE,
        os.path.join(OUTPUT_DIR, "output_users.txt"),
        header_lines=[
            "Job 3 Output : User Activity Count",
            f"Input File   : {DATA_FILE}",
            f"Generated    : {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "Mapper       : mapper_users.py  (emits User_ID -> 1 for each log record)",
            "Reducer      : reducer_users.py (sums total requests per user)",
            "Format       : <User_ID> [TAB] <Total_Request_Count>",
        ]
    )

    print("-" * 55)

    generate_summary_chart()

    print()
    print("  Results")
    print("-" * 55)

    # Print each output file nicely
    for label, fname in [
        ("Job 1 — Page Visits",        "output_pages.txt"),
        ("Job 2 — HTTP Status Codes",  "output_status.txt"),
        ("Job 3 — User Activity (Top 10)", "output_users.txt"),
    ]:
        print(f"\n  {label}")
        print(f"  {'URL / Key':<30}  Count")
        print(f"  {'-'*40}")
        with open(os.path.join(OUTPUT_DIR, fname), "r") as f:
            lines = f.readlines()
            # For users, sort by count desc and show top 10
            if "users" in fname:
                entries = [l.strip().split("\t") for l in lines if "\t" in l]
                entries.sort(key=lambda x: int(x[1]), reverse=True)
                lines = [f"{e[0]}\t{e[1]}\n" for e in entries[:10]]
            for line in lines:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    print(f"  {parts[0]:<30}  {int(parts[1]):>6,}")

    print()
    print("=" * 55)
    print("  All jobs completed.  chart -> summary_chart.png")
    print("  Run dashboard: streamlit run app.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
