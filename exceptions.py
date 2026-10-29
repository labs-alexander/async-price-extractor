class FetchError(Exception):
	def __init__(self, response, message=None):
		self.url = response.url
		self.status = response.status_code
		self.body_snippet = response.text[:500]
		super().__init__(message or f"status {self.status} at {self.url}\nSnippet: {self.body_snippet}")


class RetryableError(FetchError):
	pass


class RateLimitedError(RetryableError):
	pass


class TimeoutCustom(RetryableError):
	pass


class BlockedError(FetchError):
	pass


class ServerError(RetryableError):
	pass


class FatalError(FetchError):
	pass


class NotFoundError(FatalError):
	pass


class UnknownError(FetchError):
	def __init__(self, response):
		super().__init__(response, message=f"status {response.status_code} not catalogued at {response.url}\nSnippet: {response.text[:500]}")


STATUS_MAP = {
	429: RateLimitedError,
	500: ServerError,
	502: ServerError,
	503: ServerError,
	504: ServerError,
	403: BlockedError,
	401: BlockedError,
	404: NotFoundError,
	410: FatalError,
	400: FatalError,
	451: FatalError,
}
