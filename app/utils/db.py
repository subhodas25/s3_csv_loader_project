import psycopg2
from contextlib import contextmanager

@contextmanager
def get_db_connection(dsn):
    conn = psycopg2.connect(dsn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def copy_csv_to_db(conn, stream):
    with conn.cursor() as cursor:
        cursor.copy_expert("COPY your_table FROM STDIN WITH CSV HEADER", stream)
