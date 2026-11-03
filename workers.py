import asyncio
from urllib.parse import urlparse

async def worker(netloc, sem):
	processed_count = 0

	while True:
		jobs = database.enqueue(netloc)
		selector = database.get_selector(netloc)
		print(f"got the job: {jobs}")
		if selector:
			print(f"got the selector: {selector}")

		if not jobs:
			print(f"no jobs. breaking now.")
			break

		for job_id, url in jobs:
			print(f"run: {processed_count}")
			jitter = calc_jitter(processed_count)
			async with sem:
				response = await fetch.fetch_info(url)
				if selector:
					print(f"using selector: {selector}")
					price_tag = parser.extract_element(response.text, selector)
					price = price_tag.text
					print(f"price aquired using selector {price}")
				else:
					candidates = parser.get_price_candidates(response.text) # antigo get_price
					price, price_tag = parser.choose_price(candidates)
					selector = parser.build_css_selector(price_tag)

				save_result(job_id, price, selector)
				processed_count += 1
				await asyncio.sleep(jitter)



def save_result(job_id, price, selector, selector_type="css"):
	if price:
		database.update_job(job_id=job_id, price=price, status="processed", selector_value=selector, selector_type=selector_type)
	else:
		print(f"failed: preço nao encontrado {price}")
		database.update_job(job_id=job_id, status="failed")
