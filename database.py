import os
import asyncio
from dotenv import load_dotenv
import aiosqlite
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import config

load_dotenv()
DB_PATH = os.getenv("DB_PATH")


@asynccontextmanager
async def get_cursor(db_path=DB_PATH, isolation_level="DEFERRED"):
	con =  await aiosqlite.connect(db_path, isolation_level=isolation_level)

	try:
		cur = await con.cursor()
		yield cur
		await con.commit()

	except Exception:
		await con.rollback()
		raise

	finally:
		await con.close()


async def setup_database(db_path=DB_PATH):
	async with get_cursor(db_path) as cur:	
		await cur.execute("""CREATE TABLE IF NOT EXISTS jobs (

			id INTEGER PRIMARY KEY AUTOINCREMENT,
			url TEXT,
			netloc TEXT,
			status TEXT DEFAULT "pending",
			price TEXT DEFAULT '$0',
			selector_type TEXT,
			selector_value TEXT,
			created_at TEXT DEFAULT CURRENT_TIMESTAMP,
			updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
			attempts INTEGER DEFAULT 0
			)""")

		await cur.execute("CREATE INDEX IF NOT EXISTS idx_jobs_url_created ON jobs(url, created_at);")
		await cur.execute("""
		    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_url 
		    ON jobs(url) 
		    WHERE status != 'done';
		""")


async def insert_job(url, db_path=DB_PATH):
	netloc = urlparse(url).netloc
	async with get_cursor(db_path) as cur:
		await cur.execute("""INSERT OR IGNORE INTO jobs (url, netloc) VALUES (?, ?)""", (url, netloc))


async def update_job(job_id, db_path=DB_PATH, **kwargs):

	if not kwargs:
		return []

	fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
	values = list(kwargs.values()) + [job_id]
	query = f"""UPDATE jobs SET {fields}, updated_at = CURRENT_TIMESTAMP
			WHERE id = ?
				"""
	async with get_cursor(db_path, isolation_level="IMMEDIATE") as cur:
		await cur.execute(query, values)
		return cur.rowcount


async def get_pending_netlocs(db_path=DB_PATH):
	async with get_cursor(db_path) as cur:
		await cur.execute("SELECT DISTINCT netloc FROM jobs WHERE status = ?", ("pending",))
		results = await cur.fetchall()
		return [row[0] for row in results]


async def enqueue(netloc, limit=20, db_path=DB_PATH):
	async with get_cursor(db_path, isolation_level="IMMEDIATE") as cur:
		await cur.execute("""UPDATE jobs
			SET status = ?
			WHERE id IN (
				SELECT id FROM jobs
				WHERE netloc = ? AND status = ?
				LIMIT ?
				)
			RETURNING id, url;
			""", ("processing", netloc, "pending", limit))
		results = await cur.fetchall()
		return results


async def get_selector(netloc, db_path=DB_PATH):
	async with get_cursor(db_path) as cur:
		await cur.execute("SELECT selector_value FROM jobs WHERE netloc = ? AND selector_value IS NOT NULL LIMIT 1", (netloc,))
		results = await cur.fetchone()
		return results[0] if results else None


async def get_attempts(job_id, db_path=DB_PATH):
	async with get_cursor(db_path) as cur:
		await cur.execute("SELECT attempts FROM jobs WHERE id = ?", (job_id,))
		result = await cur.fetchone()
		return result[0] if result else 0

#=====================================================================
# 	 							FLOW TEST
#=====================================================================

async def test():
    await setup_database()

    for url in getattr(config, "URLS", []):
        await insert_job(url)

    async with get_cursor() as cur:
        sim = input("resete? ")
        if sim == "s":
            await cur.execute("UPDATE jobs SET status = 'pending'")

        await cur.execute("SELECT id, netloc, price, status, selector_value, selector_type FROM jobs")
        results = await cur.fetchall()

        for r in results:
            print(r)


if __name__ == "__main__":
    asyncio.run(test())
