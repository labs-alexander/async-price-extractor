import asyncio

from async_tls_client import AsyncSession

import config
from exceptions import STATUS_MAP, BlockedError, RateLimitedError


def create_session(impersonate=config.IMPERSONATE):
	return AsyncSession(client_identifier=impersonate)


async def fetch_info(url, method="GET", session):
	response = await session.execute_request(url=url, method=method)
	return classify_response(response)


def classify_response(response):
	code = response.status_code
	print(response)
	if 200 <= code < 300:
		return response

	error = STATUS_MAP.get(code)

	raise error(response)
