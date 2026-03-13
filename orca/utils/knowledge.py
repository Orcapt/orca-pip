"""
Knowledge Stores Helper
=======================

Helper class for easy access to knowledge stores from Orca requests.

Usage:
    from orca.utils.knowledge import KnowledgeStores

    stores = KnowledgeStores(data.knowledge_stores)
    store_ids = stores.get_store_ids()

    # Use with Gemini FileSearch:
    import google.genai as genai
    tool = genai.types.Tool(
        file_search=genai.types.FileSearch(file_search_store_names=store_ids)
    )
"""

from typing import List, Optional

from ..domain.models import KnowledgeStore


class KnowledgeStores:
    """Helper class for working with knowledge stores from an Orca request."""

    def __init__(self, stores_list):
        if not stores_list:
            self._stores: List[KnowledgeStore] = []
        else:
            self._stores = [
                s if isinstance(s, KnowledgeStore) else KnowledgeStore(**s)
                for s in stores_list
            ]

    def get_store_ids(self) -> List[str]:
        """Get all store IDs, ready to pass to genai.types.FileSearch."""
        return [s.store_id for s in self._stores]

    def get_by_name(self, name: str) -> Optional[KnowledgeStore]:
        """Find a store by its display name."""
        return next((s for s in self._stores if s.name == name), None)

    def get_by_provider(self, provider: str) -> List[KnowledgeStore]:
        """Filter stores by provider type."""
        return [s for s in self._stores if s.provider == provider]

    def is_empty(self) -> bool:
        """Check if there are no knowledge stores."""
        return len(self._stores) == 0

    def count(self) -> int:
        """Return the number of knowledge stores."""
        return len(self._stores)

    def to_list(self) -> List[KnowledgeStore]:
        """Return the raw list of KnowledgeStore objects."""
        return list(self._stores)
