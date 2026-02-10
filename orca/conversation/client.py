"""
Orca Conversation Client
=========================

Facade for external conversation API operations.
Delegates to BaseConversationClient for HTTP communication.

Supports two initialisation modes:
1. **From ChatMessage** (inside an agent): auto-derives base_url from ``data.url``.
2. **Manual** (standalone/external): pass ``token`` and ``base_url`` explicitly.
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse

from .base_client import BaseConversationClient, ConversationException


class OrcaConversation:
    """
    Orca Conversation Client (Facade Pattern).

    Example – inside an agent::

        conv = OrcaConversation(data=data)
        conv.rename(thread_id=data.thread_id, title="New title")

    Example – standalone::

        conv = OrcaConversation(
            token="workspace-token",
            base_url="https://api.orcaplatform.ai/v1/external",
        )
        result = conv.create(
            project_uuid="abc-123",
            title="Chat",
            model="gpt-4",
            user_id_external="ext-user-1",
        )
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        data: Any = None,
        timeout: int = 30,
    ):
        """
        Initialise the conversation client.

        Args:
            token: Workspace token (sent as ``X-Workspace`` header).
                   Not required when ``data`` is provided and contains headers
                   with the token.
            base_url: External API base URL.  When *data* is provided this is
                      auto-derived from ``data.url`` if not given explicitly.
            data: A ``ChatMessage`` (or any object with ``.url`` and optional
                  ``.headers``).  When supplied the client will extract the
                  base URL and any extra headers automatically.
            timeout: HTTP request timeout in seconds.

        Raises:
            ValueError: When neither ``token`` nor ``data`` provides enough
                        information to authenticate.
        """
        extra_headers: Optional[Dict[str, str]] = None

        if data is not None:
            # Derive base_url from the request URL when not given explicitly
            if base_url is None and hasattr(data, "url") and data.url:
                parsed = urlparse(data.url)
                base_url = f"{parsed.scheme}://{parsed.netloc}/v1/external"

            # Carry over any request headers (e.g. Authorization)
            if hasattr(data, "headers") and data.headers:
                extra_headers = dict(data.headers)

            # Try to pull the token from the request headers
            if token is None and extra_headers:
                token = extra_headers.get("X-Workspace") or extra_headers.get("x-workspace")

        # Fallback defaults
        if base_url is None:
            base_url = "https://api.orcapt.com/v1/external"

        if not token:
            raise ValueError(
                "A workspace token is required. Provide 'token' directly or "
                "pass a ChatMessage 'data' whose headers contain 'X-Workspace'."
            )

        self._client = BaseConversationClient(
            token=token,
            base_url=base_url,
            timeout=timeout,
            extra_headers=extra_headers,
        )

    # ==================== Conversation CRUD ====================

    def create(
        self,
        project_uuid: str,
        title: str,
        model: str,
        user_id_external: str,
        content: Optional[str] = None,
        force_search: bool = False,
        active_analysis: bool = False,
        file: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Create a new conversation in a project.

        Args:
            project_uuid: UUID of the project.
            title: Conversation title.
            model: AI model identifier (e.g. ``gpt-4``).
            user_id_external: External user ID (``users.external_id``).
            content: Optional initial user message.
            force_search: Force knowledge-base search.
            active_analysis: Enable active analysis.
            file: Optional file to attach (file-like object).

        Returns:
            API response with created conversation data.
        """
        endpoint = f"/projects/{project_uuid}/conversations"

        if file is not None:
            # Multipart upload
            data = {
                "title": title,
                "model": model,
                "user_id_external": user_id_external,
            }
            if force_search:
                data["force_search"] = "true"
            if active_analysis:
                data["active_analysis"] = "true"
            if content is not None:
                data["content"] = content
            return self._client.post(endpoint, data=data, files={"file": file})

        payload: Dict[str, Any] = {
            "title": title,
            "model": model,
            "user_id_external": user_id_external,
            "force_search": force_search,
            "active_analysis": active_analysis,
        }
        if content is not None:
            payload["content"] = content

        return self._client.post(endpoint, json_data=payload)

    def rename(self, thread_id: str, title: str) -> Dict[str, Any]:
        """
        Rename (update) an existing conversation.

        Args:
            thread_id: The conversation's ``thread_id``.
            title: New title for the conversation.

        Returns:
            API response confirming the update.
        """
        endpoint = f"/conversations/{thread_id}"
        return self._client.put(endpoint, json_data={"title": title})

    def list(
        self,
        project_uuid: str,
        search: Optional[str] = None,
        model: Optional[str] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List conversations in a project.

        Args:
            project_uuid: UUID of the project.
            search: Filter by title (partial match).
            model: Filter by model name (partial match).
            user: Filter by user name (partial match).

        Returns:
            Paginated list of conversations.
        """
        endpoint = f"/projects/{project_uuid}/conversations"
        params: Dict[str, str] = {}
        if search is not None:
            params["search"] = search
        if model is not None:
            params["model"] = model
        if user is not None:
            params["user"] = user

        return self._client.get(endpoint, params=params or None)

    def get(self, project_uuid: str, thread_id: str) -> Dict[str, Any]:
        """
        Get a single conversation.

        Args:
            project_uuid: UUID of the project.
            thread_id: The conversation's ``thread_id``.

        Returns:
            Conversation data.
        """
        endpoint = f"/projects/{project_uuid}/conversations/{thread_id}"
        return self._client.get(endpoint)

    def delete(self, project_uuid: str, thread_id: str) -> Dict[str, Any]:
        """
        Delete a conversation.

        Args:
            project_uuid: UUID of the project.
            thread_id: The conversation's ``thread_id``.

        Returns:
            API response confirming deletion.
        """
        endpoint = f"/projects/{project_uuid}/conversations/{thread_id}"
        return self._client.delete(endpoint)

    # ==================== Messages ====================

    def list_messages(self, thread_id: str) -> Dict[str, Any]:
        """
        List all messages in a conversation.

        Args:
            thread_id: The conversation's ``thread_id``.

        Returns:
            List of messages with model info.
        """
        endpoint = f"/conversations/{thread_id}/messages"
        return self._client.get(endpoint)

    def send_message(
        self,
        thread_id: str,
        content: Optional[str] = None,
        model: Optional[str] = None,
        force_search: Optional[bool] = None,
        active_analysis: Optional[bool] = None,
        file: Optional[Any] = None,
        is_data: bool = False,
    ) -> Dict[str, Any]:
        """
        Send (inject) a message into an existing conversation.

        Args:
            thread_id: The conversation's ``thread_id``.
            content: Message content.
            model: Optional model override.
            force_search: Optional force knowledge-base search override.
            active_analysis: Optional active analysis override.
            file: Optional file attachment (file-like object).
            is_data: Whether the message is a data message (default False).

        Returns:
            API response with the created message and streaming info.
        """
        endpoint = f"/conversations/{thread_id}/messages"

        if file is not None:
            data: Dict[str, str] = {
                "isData": str(is_data).lower(),
            }
            if content is not None:
                data["content"] = content
            if model is not None:
                data["model"] = model
            if force_search is not None:
                data["force_search"] = str(force_search).lower()
            if active_analysis is not None:
                data["active_analysis"] = str(active_analysis).lower()
            return self._client.post(endpoint, data=data, files={"file": file})

        payload: Dict[str, Any] = {
            "isData": is_data,
        }
        if content is not None:
            payload["content"] = content
        if model is not None:
            payload["model"] = model
        if force_search is not None:
            payload["force_search"] = force_search
        if active_analysis is not None:
            payload["active_analysis"] = active_analysis

        return self._client.post(endpoint, json_data=payload)
