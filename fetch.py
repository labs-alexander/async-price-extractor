from async_tls_client import AsyncSession
import config
from exceptions import STATUS_MAP, RateLimitedError, BlockedError
import asyncio


async def fetch_info(url, method="GET", impersonate=config.IMPERSONATE):
	async with AsyncSession(client_identifier=impersonate) as session:
		response = await session.execute_request(method=method, url=url)
		return classify_response(response)


def classify_response(response):
	code = response.status_code
	print(response)
	if 200 <= code < 300:
		return response

	error = STATUS_MAP.get(code)

	raise error(response)
