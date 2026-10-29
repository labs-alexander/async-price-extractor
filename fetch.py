from async_tls_client import AsyncSession
import config


async def fetch_info(url, method="GET", impersonate=config.IMPERSONATE):
	async with AsyncSession(client_identifier=impersonate) as session:
		response = await session.execute_request(method=method, url=url)
		return response
