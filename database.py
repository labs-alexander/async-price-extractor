import sqlite3
from contextlib import contextmanager

DB_PATH = ""

@contextmanager
def get_cursor(db_path=DB_PATH, isolation_level="DEFERRED"):
	con = sqlite3.connect(db_path, isolation_level=isolation_level)
	cur = con.cursor()

	try:
		yield cur
		con.commit()

	except Exception:
		con.rollback()
		raise

	finally:
		con.close()


def setup_database(db_path=DB_PATH):
	with get_cursor(db_path) as cur:	
		cur.execute("""CREATE TABLE IF NOT EXISTS jobs (

			id INTEGER PRIMARY KEY AUTOINCREMENT,
			url TEXT,
			netloc TEXT,
			status TEXT DEFAULT "pending",
			price TEXT DEFAULT 'PREÇO AQUI',
			selector_type TEXT,
			selector_value TEXT,
			created_at TEXT DEFAULT CURRENT_TIMESTAMP,
			updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
			attempts INTEGER DEFAULT 0
			)""")

		cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_url_created ON jobs(url, created_at);")
		cur.execute("""
		    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_url 
		    ON jobs(url) 
		    WHERE status != 'done';
		""")


def insert_job(url, db_path=DB_PATH):
	netloc = urlparse(url).netloc
	with get_cursor(db_path) as cur:
		cur.execute("""INSERT OR IGNORE INTO jobs (url, netloc) VALUES (?, ?)""", (url, netloc))


def update_job(job_id, db_path=DB_PATH, **kwargs):

	if not kwargs:
		return []

	fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
	values = list(kwargs.values()) + [job_id]
	query = f"""UPDATE jobs SET {fields}, updated_at = CURRENT_TIMESTAMP
			WHERE id = ?
				"""
	with get_cursor(db_path, isolation_level="IMMEDIATE") as cur:
		cur.execute(query, values)
		return cur.rowcount


def get_pending_netlocs(db_path=DB_PATH):
	with get_cursor(db_path) as cur:
		cur.execute("SELECT DISTINCT netloc FROM jobs WHERE status = ?", ("pending",))
		return [row[0] for row in cur.fetchall()]


def enqueue(netloc, limit=20, db_path=DB_PATH):
	with get_cursor(db_path, isolation_level="IMMEDIATE") as cur:
		cur.execute("""UPDATE jobs
			SET status = ?
			WHERE id IN (
				SELECT id FROM jobs
				WHERE netloc = ? AND status = ?
				LIMIT ?
				)
			RETURNING id, url;
			""", ("processing", netloc, "pending", limit))

		return cur.fetchall()


def get_selector(netloc, db_path=DB_PATH):
	with get_cursor(db_path) as cur:
		cur.execute("SELECT selector_value FROM jobs WHERE netloc = ?", (netloc,))
		return cur.fetchone()[0]


if __name__ == "__main__":
	test()
