import asyncio
from urllib.parse import urlparse
from dotenv import load_env
import logging
import os
from bs4 import Tag

logger = logging.getLogger(__name__)
SEM = os.getenv("SEMAPHORE")

async def worker(netloc, sem):
	processed_count = 0

	while True:
		jobs = await database.enqueue(netloc)
		selector = await database.get_selector(netloc)

		if not jobs:
			logger.info("No jobs found. breaking now.")
			break

		for job_id, url in jobs:
			jitter = calc_jitter(processed_count)
			price, selector = await process_job(url, sem, selector)
			await save_result(job_id, price, selector)
			await asyncio.sleep(jitter)
			processed_count += 1


async def save_result(job_id, price, selector, selector_type="css"):
	if price:
		if isinstance(price, Tag):
			price = price.text
		await database.update_job(job_id=job_id, price=price, status="processed", selector_value=selector, selector_type=selector_type)
	else:
		print(f"failed: preço nao encontrado {price}")
		await database.update_job(job_id=job_id, status="pending")


