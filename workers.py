import asyncio
import logging
import os
from random import uniform
import signal

from dotenv import load_dotenv

import database
import fetch
import parser

logger = logging.getLogger(__name__)


load_dotenv()
SEM = int(os.getenv("SEMAPHORE"))
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS"))


async def worker(netloc, sem):
	processed_count = 0
	sem = asyncio.Semaphore(sem)

	async with fetch.create_session() as session:
		while True:
			jobs = await database.enqueue(netloc)
			selector = await database.get_selector(netloc)

			if not jobs:
				logger.info("No jobs found. breaking now.")
				break

			for job_id, url in jobs:
				jitter = calc_jitter(processed_count)
				try:
					price, selector = await process_job(url=url, sem=sem, selector=selector, job_id=job_id, session=session)
					await save_result(job_id, price, selector)
				except Exception as e:
					logger.error(f"job {job_id} failed: {e}")
				processed_count += 1
				await asyncio.sleep(jitter)

#=====================================================================
# 	 						    HELPERS
#=====================================================================

async def handle_failure(job_id):
	attempts = await database.get_attempts(job_id)
	if attempts >= MAX_ATTEMPTS:
		await database.update_job(job_id, status="failed")
	else:
		await database.update_job(job_id, status="pending", attempts=attempts + 1)


async def process_job(job_id, url, sem, selector, session):
	try:
		async with sem:
			response = await fetch.fetch_info(session=session, url=url)
			if selector:
				price_tag = parser.extract_element(response.text, selector)
				if price_tag:
					price = price_tag.text
				else:
					selector = None

			if not selector:
				candidates = parser.get_price_candidates(response.text)
				result = parser.choose_price(candidates)
				if not result:
					return None, None
				price, price_tag = result
				selector = parser.build_css_selector(price_tag)

			return price, selector
	except Exception:
		handle_failure(job_id)
		raise
			

def calc_jitter(processed_count):
	return uniform(3,5)


async def save_result(job_id, price, selector, selector_type="css"):
	if price:
		await database.update_job(job_id=job_id, price=price, status="processed", selector_value=selector, selector_type=selector_type)
	else:
		handle_failure(job_id)


async def shutdown(db_path=database.DB_PATH):
	logger.info("Shutting down, resetting stuck jobs...")
	async with database.get_cursor(db_path) as cur:
		await cur.execute("UPDATE jobs SET status = 'pending' WHERE status = 'processing'")

#=====================================================================
# 	 							FLOW TEST
#=====================================================================

async def main():
    netlocs = await database.get_pending_netlocs()
    tasks = [asyncio.create_task(worker(netloc, SEM)) for netloc in netlocs]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(shutdown())
	
