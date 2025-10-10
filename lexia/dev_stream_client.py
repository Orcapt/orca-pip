"""
Dev Stream Client
=================

Handles streaming for local development without Centrifugo.
Uses in-memory storage and SSE (Server-Sent Events) for real-time updates.
"""

import logging
from typing import Dict, Any, Optional
from threading import Lock
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class DevStreamClient:
    """
    Development streaming client that stores messages in memory.
    Frontend can poll or use SSE to get updates.
    """
    
    # Class-level storage for streaming data (shared across instances)
    _streams: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        'chunks': [],
        'full_response': '',
        'finished': False,
        'error': None
    })
    _lock = Lock()
    
    def __init__(self):
        """Initialize the dev stream client."""
        logger.info("🔧 Dev Stream Client initialized (no Centrifugo)")
    
    @classmethod
    def get_stream(cls, channel: str) -> Dict[str, Any]:
        """
        Get the current stream state for a channel.
        
        Args:
            channel: Channel name
            
        Returns:
            Dict containing chunks, full_response, finished status, and error
        """
        with cls._lock:
            return dict(cls._streams[channel])
    
    @classmethod
    def clear_stream(cls, channel: str):
        """
        Clear a stream (useful for cleanup).
        
        Args:
            channel: Channel name
        """
        with cls._lock:
            if channel in cls._streams:
                del cls._streams[channel]
                logger.debug(f"Cleared stream for channel: {channel}")
    
    def send(self, channel: str, data: Dict[str, Any]):
        """
        Store data for a channel (dev mode simulation).
        
        Args:
            channel: Channel name
            data: Data to store
        """
        try:
            with self._lock:
                stream = self._streams[channel]
                
                # Handle delta (streaming chunk)
                if 'delta' in data and data.get('delta'):
                    stream['chunks'].append(data['delta'])
                    stream['full_response'] += data['delta']
                    logger.debug(f"📝 Dev stream delta added to {channel}: {len(data['delta'])} chars")
                
                # Handle completion
                if data.get('finished'):
                    stream['finished'] = True
                    if 'full_response' in data:
                        stream['full_response'] = data['full_response']
                    logger.info(f"✅ Dev stream completed for {channel}")
                
                # Handle error
                if data.get('error'):
                    stream['error'] = data.get('content', 'An error occurred')
                    stream['finished'] = True
                    logger.error(f"❌ Dev stream error for {channel}: {stream['error']}")
                
                # Store the complete message data
                stream['last_message'] = data
                
        except Exception as e:
            logger.error(f"Error in dev stream send to {channel}: {e}")
    
    def send_delta(self, channel: str, uuid: str, thread_id: str, delta: str):
        """
        Send a streaming delta message (dev mode).
        
        Args:
            channel: Channel name
            uuid: Response UUID
            thread_id: Thread ID
            delta: Text delta to send
        """
        data = {
            'delta': delta,
            'finished': False,
            'uuid': uuid,
            'thread_id': thread_id
        }
        self.send(channel, data)
        # Also log to console for immediate visibility in dev
        print(delta, end='', flush=True)
    
    def send_completion(self, channel: str, uuid: str, thread_id: str, full_response: str):
        """
        Send a completion signal (dev mode).
        
        Args:
            channel: Channel name
            uuid: Response UUID
            thread_id: Thread ID
            full_response: Complete response text
        """
        data = {
            'finished': True,
            'uuid': uuid,
            'thread_id': thread_id,
            'full_response': full_response
        }
        self.send(channel, data)
        print()  # New line after completion in console
    
    def send_error(self, channel: str, uuid: str, thread_id: str, error_message: str):
        """
        Send an error notification (dev mode).
        
        Args:
            channel: Channel name
            uuid: Response UUID
            thread_id: Thread ID
            error_message: Error message
        """
        data = {
            'error': True,
            'content': error_message,
            'finished': True,
            'uuid': uuid,
            'thread_id': thread_id,
            'status': 'FAILED',
            'role': 'developer'
        }
        self.send(channel, data)

