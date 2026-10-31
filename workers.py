import asyncio
from urllib.parse import urlparse

async def worker(netloc, queue, sem):
	processed_count = 0
	while not queue.empty():
		job_id, url = await queue.get()
		jitter = calc_jitter(processed_count)

		async with sem:
			response = await fetch.fetch_info(url)
			print(response.status_code)
			save_result(job_id, response)
			await asyncio.sleep(jitter)

		queue.task_done()
		processed_count += 1


def save_result(response):
	price = parser.get_price(response.text)
	
	if price:
		print(price)
		database.update_job(job_id=job_id, price=price[1].text, status="processed")
	else:
		print("failed")
		database.update_job(job_id=job_id, status="failed")
