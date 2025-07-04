"""
HTTP utility for sending asynchronous requests using aiohttp.

Includes:
- Timeout handling (120 seconds total)
- Automatic JSON parsing via orjson
- Logging of request duration and errors
"""

from aiohttp import ClientSession, ClientError, ClientTimeout
from time import time
from orjson import orjson, JSONDecodeError

from app.common.logger import log


async def send_request(method: str, url: str, **kwargs) -> dict:
    """
    Sends an asynchronous HTTP request using aiohttp with a 120-second timeout,
    parses the response as JSON, and logs execution time and errors.

    Args:
        method (str): HTTP method (e.g., "GET", "POST").
        url (str): The target URL for the request.
        **kwargs: Optional keyword arguments passed to aiohttp (e.g., headers, params, json, etc.).

    Returns:
        dict: Parsed JSON response if successful, otherwise an empty dict.
    """
    start = time()
    try:
        timeout = ClientTimeout(total=120)
        async with ClientSession(timeout=timeout) as session:
            async with session.request(method=method, url=url, **kwargs) as resp:
                response_text = await resp.text()
                try:
                    data = orjson.loads(response_text)
                except JSONDecodeError:
                    log(f"Invalid JSON [{resp.status}]: {response_text} - {url}", force=True)
                    data = {}

                log(f"{method} {url} - {int((time() - start) * 1000)} ms")
                return data
    except ClientError as e:
        log(f"Connection error: {e} - {url}", force=True)
        return {}
