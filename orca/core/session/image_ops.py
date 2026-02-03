"""
Image Operations
================

Handles image operations for a session.
Ultra-focused: ONLY image handling.
"""

import logging
import os
import re
import requests
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ImageOperations:
    """
    Manages image streaming.
    
    Ultra-focused on image operations only.
    Single Responsibility: Image handling.
    """
    
    def __init__(self, stream_func, handler=None, data=None):
        """
        Initialize image operations.
        
        Args:
            stream_func: Function to stream content
            handler: Optional parent handler (for API calls)
            data: Optional request data (for API base URL and headers)
        """
        self._stream = stream_func
        self._handler = handler
        self._data = data
    
    def send(self, image_input: str) -> None:
        """
        Stream image with Orca markers.
        
        Accepts either:
        - Image URL (string starting with http:// or https://)
        - Base64 string (data URI format: data:image/...;base64,...)
        
        If base64 is provided, it will be uploaded to media API first.
        
        Args:
            image_input: Image URL or base64 string
        """
        if not image_input:
            logger.warning("Image input is empty, skipping")
            return
        
        # Determine if input is base64 or URL
        image_url = self._process_image_input(image_input)
        
        if not image_url:
            logger.error("Failed to process image input")
            return
        
        # Wrap URL in Orca markers and stream
        payload = f"[orca.image.start]{image_url}[orca.image.end]"
        self._stream(payload)
    
    def _process_image_input(self, image_input: str) -> Optional[str]:
        """
        Process image input - upload base64 to media API or return URL as-is.
        
        Args:
            image_input: Image URL or base64 string
            
        Returns:
            Image URL (either original or from media API)
        """
        # Check if it's a URL (starts with http:// or https://)
        if image_input.startswith(('http://', 'https://')):
            return image_input
        
        # Check if it's base64 (data URI format or raw base64)
        is_base64 = (
            image_input.startswith('data:image/') or  # Data URI format
            (len(image_input) > 50 and not image_input.startswith('http') and 
             all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in image_input[:100]))  # Raw base64
        )
        
        if is_base64:
            # Try to upload base64 to media API
            return self._upload_base64_to_media_api(image_input)
        
        # If it doesn't match patterns, assume it's a URL
        return image_input
    
    def _upload_base64_to_media_api(self, base64_data: str) -> Optional[str]:
        """
        Upload base64 image to media API and return the URL.
        
        Args:
            base64_data: Base64 string (with or without data URI prefix)
            
        Returns:
            Media API URL or None if upload fails
        """
        try:
            # Extract API base URL
            api_base_url = self._extract_api_base_url()
            
            # Get headers for authentication
            headers = getattr(self._data, 'headers', {}) if self._data else {}
            headers['Content-Type'] = 'application/json'
            
            # Prepare base64 - ensure it has data URI prefix if needed
            if not base64_data.startswith('data:'):
                # Assume it's image/png if no prefix
                base64_data = f"data:image/png;base64,{base64_data}"
            
            # Call media API
            endpoint = f"{api_base_url}/api/v1/media"
            payload = {
                'base64': base64_data
            }
            
            # Add conversation_id from request data (automatically included from request)
            if self._data:
                conversation_id = getattr(self._data, 'conversation_id', None)
                if conversation_id:
                    payload['conversation_id'] = conversation_id
                
                # Add agent_id if available (optional)
                agent_id = getattr(self._data, 'agent_id', None)
                if agent_id:
                    payload['agent_id'] = agent_id
            
            logger.info(f"Uploading base64 image to media API: {endpoint}")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                # Handle both response formats: {'success': True, 'data': {'url': ...}} 
                # and {'result': {'url': ...}, 'message': '...'}
                media_url = None
                if result.get('success') and result.get('data', {}).get('url'):
                    media_url = result['data']['url']
                elif result.get('result', {}).get('url'):
                    media_url = result['result']['url']
                
                if media_url:
                    logger.info(f"✅ Image uploaded successfully, URL: {media_url[:50]}...")
                    return media_url
                else:
                    logger.error(f"Media API returned success but no URL found: {result}")
            else:
                logger.error(f"Media API upload failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to upload base64 to media API: {e}")
        
        return None
    
    def _extract_api_base_url(self) -> str:
        """
        Extract API base URL from request data or environment.
        
        Returns:
            API base URL string
        """
        if self._data and hasattr(self._data, 'url') and self._data.url:
            parsed = urlparse(self._data.url)
            return f"{parsed.scheme}://{parsed.netloc}"
        
        return os.environ.get('ORCA_API_BASE_URL', 'http://localhost')
    
    # Alias for convenience
    pass_image = send

