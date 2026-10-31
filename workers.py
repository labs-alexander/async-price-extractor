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
			print(f"sleeped for {jitter} secs")

		queue.task_done()
		processed_count += 1
