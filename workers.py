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
	sem = asyncio.Semaphore(sem)

	while True:
		jobs = await database.enqueue(netloc)
		selector = await database.get_selector(netloc)

		if not jobs:
			logger.info("No jobs found. breaking now.")
			break

		for job_id, url in jobs:
			jitter = calc_jitter(processed_count)
			price, selector = await process_job(url=url, sem=sem, selector=selector, job_id=job_id)
			await save_result(job_id, price, selector)
			processed_count += 1
			await asyncio.sleep(jitter)
			



#=====================================================================
# 	 						    HELPERS
#=====================================================================

async def process_job(job_id, url, sem, selector):
	try:
		async with sem:
			async with fetch.create_session() as session:)
				response = await fetch.fetch_info(session=session, url=url)
				if selector:
					price_tag = parser.extract_element(response.text, selector)
					if price_tag:
						price = price_tag.text
					else:
						selector = None

				if not selector:
					candidates = parser.get_price_candidates(response.text)
					price, price_tag = parser.choose_price(candidates)
					selector = parser.build_css_selector(price_tag)

				return price, selector
	except Exception:
		await database.update_job(job_id, status="pending")
		raise
		

async def save_result(job_id, price, selector, selector_type="css"):
	if price:
		if isinstance(price, Tag):
			price = price.text
		await database.update_job(job_id=job_id, price=price, status="processed", selector_value=selector, selector_type=selector_type)
	else:
		print(f"failed: preço nao encontrado {price}")
		await database.update_job(job_id=job_id, status="pending")


