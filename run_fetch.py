import yaml
import duckdb
from pathlib import Path

def run_job(job):
    # Ensure destination folder exists
    dest_path = Path(job["destination"])
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to DuckDB and load CSV directly
    con = duckdb.connect(dest_path)
    con.execute(f"""
        CREATE OR REPLACE TABLE {job['table']} AS
        SELECT * FROM read_csv_auto('{job["source_url"]}')
    """)

    print(f"✔ Saved table '{job['table']}' to: {dest_path}")

def main():
    with open("fetch_jobs.yaml", "r") as f:
        config = yaml.safe_load(f)
    for job in config["jobs"]:
        run_job(job)

if __name__ == "__main__":
    main()