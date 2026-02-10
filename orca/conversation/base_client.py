"""
Conversation Base Client
========================

Low-level HTTP client for the external conversation API.
Single Responsibility: HTTP communication only.
"""

import requests
from typing import Optional, Dict, Any


class ConversationException(Exception):
    """Base exception for conversation API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BaseConversationClient:
    """
    Base HTTP client for the external conversation API.

    Responsibilities:
    - HTTP request handling
    - Error handling
    - Authentication headers

    Auth: Single ``X-Workspace`` header carrying the workspace token.
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.orcapt.com/v1/external",
        timeout: int = 30,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialise the base client.

        Args:
            token: Workspace token (sent as ``X-Workspace`` header).
            base_url: Base URL for the external API (without trailing slash).
            timeout: Request timeout in seconds.
            extra_headers: Optional additional headers to merge into every request.
        """
        if not token:
            raise ValueError("Token is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers: Dict[str, str] = {
            "X-Workspace": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if extra_headers:
            self.headers.update(extra_headers)

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the external API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (appended to ``base_url``).
            data: Form data.
            files: Files to upload.
            params: Query parameters.
            json_data: JSON payload.

        Returns:
            Parsed JSON response.

        Raises:
            ConversationException: On HTTP or network errors.
        """
        url = f"{self.base_url}{endpoint}"

        try:
            kwargs: Dict[str, Any] = {
                "headers": self.headers.copy(),
                "timeout": self.timeout,
            }

            if params:
                kwargs["params"] = params
            if json_data:
                kwargs["json"] = json_data
                kwargs["headers"]["Content-Type"] = "application/json"
            if data:
                kwargs["data"] = data
            if files:
                kwargs["files"] = files
                # Let requests set the multipart boundary
                kwargs["headers"].pop("Content-Type", None)

            response = requests.request(method, url, **kwargs)

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    message = error_data.get("message", f"HTTP {response.status_code}")
                except Exception:
                    error_data = None
                    message = f"HTTP {response.status_code}: {response.text[:200]}"

                raise ConversationException(
                    message,
                    status_code=response.status_code,
                    response=error_data,
                )

            try:
                return response.json()
            except Exception:
                return {"status": "success"}

        except requests.exceptions.RequestException as e:
            raise ConversationException(f"Request failed: {str(e)}") from e

    # -------------------- convenience wrappers --------------------

    def get(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)
