import os
import io
import logging
import boto3
import psycopg2
from contextlib import contextmanager
from prometheus_client import start_http_server, Counter, Histogram
from tenacity import retry, wait_exponential, stop_after_attempt
from app.config import S3_BUCKET, PG_DSN
from app.utils.s3 import list_csv_files, download_csv_file, delete_csv_file
from app.utils.db import get_db_connection, copy_csv_to_db

logging.basicConfig(level=logging.INFO)

FILES_PROCESSED = Counter("csv_files_processed_total", "CSV files processed", ["status"])
ROWS_INSERTED = Counter("rows_inserted_total", "Rows inserted into Postgres")
PROCESS_TIME = Histogram("process_duration_seconds", "Time taken to process CSV files")

@retry(wait=wait_exponential(multiplier=2, min=5, max=30), stop=stop_after_attempt(3))
@PROCESS_TIME.time()
def process_csv_file(bucket, key):
    logging.info(f"Processing file: s3://{bucket}/{key}")
    csv_data = download_csv_file(bucket, key)
    stream = io.StringIO(csv_data)

    with get_db_connection(PG_DSN) as conn:
        copy_csv_to_db(conn, stream)
        ROWS_INSERTED.inc(stream.getvalue().count('\n') - 1)

    delete_csv_file(bucket, key)
    FILES_PROCESSED.labels("success").inc()
    logging.info(f"Deleted file: s3://{bucket}/{key}")

def main():
    for key in list_csv_files(S3_BUCKET):
        try:
            process_csv_file(S3_BUCKET, key)
        except Exception as e:
            logging.exception(f"Failed to process {key}")
            FILES_PROCESSED.labels("failure").inc()

if __name__ == "__main__":
    start_http_server(8000)
    main()
