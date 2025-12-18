"""
HTTP client implementations for synchronous and asynchronous operations.

This module provides both sync and async HTTP clients using httpx library.
"""

from typing import Any

import httpx

from pydantic import BaseModel, Field


class HttpClientConfig(BaseModel):
    base_url: str | None = Field(None, env="HTTP_BASE_URL")
    timeout: float = Field(30.0, env="HTTP_TIMEOUT")
    headers: dict[str, str] | None = Field(None, env="HTTP_HEADERS")
    verify_ssl: bool = Field(True, env="HTTP_VERIFY_SSL")
    follow_redirects: bool = Field(True, env="HTTP_FOLLOW_REDIRECTS")


class AsyncHTTPClient:
    """
    Asynchronous HTTP client wrapper around httpx.

    Example:
        ```python
        async with AsyncHTTPClient(base_url="https://api.example.com") as client:
            response = await client.get("/endpoint")
            print(response.json())
        ```
    """

    def __init__(
        self,
        config: HttpClientConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize async HTTP client.

        Args:
            config: HttpClientConfig object, dict, or None (uses kwargs)
            **kwargs: Config parameters (base_url, timeout, headers, verify_ssl, follow_redirects)
        """
        if isinstance(config, HttpClientConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = HttpClientConfig(**config)
        else:
            self.config = HttpClientConfig(**kwargs)

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        """Enter async context manager and create client."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self.config.headers or {},
            verify=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager and close client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the underlying httpx async client, creating it if necessary."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self.config.headers or {},
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
            )
        return self._client

    async def close(self) -> None:
        """Close the client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send async GET request.

        Args:
            url: Request URL (absolute or relative to base_url)
            params: Query parameters
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.get(url, params=params, headers=headers, **kwargs)

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send async POST request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.post(
            url, data=data, json=json, headers=headers, **kwargs
        )

    async def put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send async PUT request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.put(
            url, data=data, json=json, headers=headers, **kwargs
        )

    async def patch(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send async PATCH request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.patch(
            url, data=data, json=json, headers=headers, **kwargs
        )

    async def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send async DELETE request.

        Args:
            url: Request URL (absolute or relative to base_url)
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.delete(url, headers=headers, **kwargs)

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send generic async HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            url: Request URL (absolute or relative to base_url)
            **kwargs: Arguments passed to httpx

        Returns:
            Response object
        """
        return await self.client.request(method, url, **kwargs)


class HTTPClient:
    """
    Synchronous HTTP client wrapper around httpx.

    Example:
        ```python
        with HTTPClient(base_url="https://api.example.com") as client:
            response = client.get("/users")
            print(response.json())
        ```
    """

    def __init__(
        self,
        config: HttpClientConfig | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize HTTP client.

        Args:
            config: HttpClientConfig object, dict, or None (uses kwargs)
            **kwargs: Config parameters (base_url, timeout, headers, verify_ssl, follow_redirects)
        """
        if isinstance(config, HttpClientConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = HttpClientConfig(**config)
        else:
            self.config = HttpClientConfig(**kwargs)

        self._client: httpx.Client | None = None

    def __enter__(self) -> "HTTPClient":
        """Enter context manager and create client."""
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=self.config.headers or {},
            verify=self.config.verify_ssl,
            follow_redirects=self.config.follow_redirects,
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager and close client."""
        if self._client:
            self._client.close()
            self._client = None

    @property
    def client(self) -> httpx.Client:
        """Get the underlying httpx client, creating it if necessary."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self.config.headers or {},
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
            )
        return self._client

    def close(self) -> None:
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send GET request.

        Args:
            url: Request URL (absolute or relative to base_url)
            params: Query parameters
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.get(url, params=params, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send POST request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.post(url, data=data, json=json, headers=headers, **kwargs)

    def put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send PUT request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.put(url, data=data, json=json, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send PATCH request.

        Args:
            url: Request URL (absolute or relative to base_url)
            data: Form data to send
            json: JSON data to send
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.patch(url, data=data, json=json, headers=headers, **kwargs)

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send DELETE request.

        Args:
            url: Request URL (absolute or relative to base_url)
            headers: Additional headers for this request
            **kwargs: Additional arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.delete(url, headers=headers, **kwargs)

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Send generic HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            url: Request URL (absolute or relative to base_url)
            **kwargs: Arguments passed to httpx

        Returns:
            Response object
        """
        return self.client.request(method, url, **kwargs)
