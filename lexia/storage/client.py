"""
Lexia Storage Client
====================

High-level storage client for Lexia platform.
Based on the Storage SDK Developer Guide.
"""

import os
import io
import json
import requests
from typing import Optional, Dict, Any, List, BinaryIO, Union
from pathlib import Path


class LexiaStorageException(Exception):
    """Base exception for storage errors"""
    pass


class LexiaStorage:
    """
    Lexia Storage S3-Compatible Client
    
    Example:
        >>> storage = LexiaStorage(
        ...     workspace='my-workspace',
        ...     token='my-token',
        ...     base_url='https://api.example.com/api/v1/storage',
        ...     mode='prod'
        ... )
        >>> 
        >>> # Create bucket
        >>> bucket = storage.create_bucket('my-bucket')
        >>> 
        >>> # Upload file
        >>> file_info = storage.upload_file('my-bucket', 'report.pdf', 'reports/2025/')
        >>> 
        >>> # Download file
        >>> storage.download_file('my-bucket', 'reports/2025/report.pdf', 'local.pdf')
    """
    
    def __init__(
        self,
        workspace: str,
        token: str,
        base_url: str = 'http://localhost:8000/api/v1/storage',
        mode: str = 'dev',
        timeout: int = 30
    ):
        """
        Initialize Lexia Storage client.
        
        Args:
            workspace: Workspace slug/handle
            token: API token
            base_url: Storage API base URL
            mode: 'dev' or 'prod'
            timeout: Request timeout in seconds
        """
        if not workspace or not token:
            raise ValueError('Workspace and token are required')
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            'x-workspace': workspace,
            'x-token': token,
            'x-mode': mode
        }
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to storage API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Form data
            files: Files to upload
            params: Query parameters
            json_data: JSON data
            
        Returns:
            Response JSON
            
        Raises:
            LexiaStorageException: On API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=json_data if json_data and not files else None,
                data=data if files or (data and not json_data) else None,
                files=files,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                message = error_data.get('message', str(e))
            except:
                message = str(e)
            raise LexiaStorageException(f"Storage API error: {message}")
        except Exception as e:
            raise LexiaStorageException(f"Request failed: {e}")
    
    # ==================== Bucket Operations ====================
    
    def create_bucket(
        self,
        name: str,
        visibility: str = 'private',
        encryption: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new bucket.
        
        Args:
            name: Bucket name
            visibility: 'public' or 'private'
            encryption: Enable encryption
            
        Returns:
            Bucket info
        """
        payload = {
            'bucket_name': name,
            'visibility': visibility,
            'encryption_enabled': encryption
        }
        response = self._request('POST', '/bucket/create', json_data=payload)
        return response.get('bucket', {})
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all buckets.
        
        Returns:
            List of buckets
        """
        response = self._request('GET', '/bucket/list')
        return response.get('buckets', [])
    
    def get_bucket(self, name: str) -> Dict[str, Any]:
        """
        Get bucket metadata.
        
        Args:
            name: Bucket name
            
        Returns:
            Bucket info
        """
        response = self._request('GET', f'/bucket/{name}')
        return response.get('bucket', {})
    
    def delete_bucket(self, name: str, force: bool = False) -> Dict[str, Any]:
        """
        Delete a bucket.
        
        Args:
            name: Bucket name
            force: Force delete even if not empty
            
        Returns:
            Response data
        """
        params = {'force': 'true'} if force else None
        return self._request('DELETE', f'/bucket/{name}', params=params)
    
    # ==================== File Operations ====================
    
    def upload_file(
        self,
        bucket: str,
        file_path: Union[str, Path],
        folder_path: str = '',
        visibility: str = 'private',
        generate_url: bool = True,
        metadata: Optional[Dict] = None,
        tags: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to bucket.
        
        Args:
            bucket: Bucket name
            file_path: Local file path
            folder_path: Destination folder in bucket
            visibility: 'public' or 'private'
            generate_url: Generate download URL
            metadata: File metadata
            tags: File tags
            
        Returns:
            File info including download URL if generate_url=True
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            data = {
                'folder_path': folder_path or '',
                'visibility': visibility,
                'generate_url': 'true' if generate_url else 'false',
            }
            
            if metadata:
                data['metadata'] = json.dumps(metadata)
            if tags:
                data['tags'] = json.dumps(tags)
            
            response = self._request('POST', f'/{bucket}/upload', data=data, files=files)
            return response.get('file', {})
    
    def upload_buffer(
        self,
        bucket: str,
        file_name: str,
        buffer: Union[bytes, BinaryIO],
        folder_path: str = '',
        visibility: str = 'private',
        generate_url: bool = True,
        metadata: Optional[Dict] = None,
        tags: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Upload from memory buffer.
        
        Args:
            bucket: Bucket name
            file_name: File name
            buffer: File content (bytes or file-like object)
            folder_path: Destination folder
            visibility: 'public' or 'private'
            generate_url: Generate download URL
            metadata: File metadata
            tags: File tags
            
        Returns:
            File info
        """
        if isinstance(buffer, bytes):
            buffer = io.BytesIO(buffer)
        
        files = {'file': (file_name, buffer)}
        data = {
            'folder_path': folder_path or '',
            'visibility': visibility,
            'generate_url': 'true' if generate_url else 'false',
        }
        
        if metadata:
            data['metadata'] = json.dumps(metadata)
        if tags:
            data['tags'] = json.dumps(tags)
        
        response = self._request('POST', f'/{bucket}/upload', data=data, files=files)
        return response.get('file', {})
    
    def list_files(
        self,
        bucket: str,
        folder_path: str = '',
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """
        List files in bucket.
        
        Args:
            bucket: Bucket name
            folder_path: Filter by folder
            page: Page number
            per_page: Items per page
            
        Returns:
            Dict with 'files' and 'pagination'
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        if folder_path:
            params['folder_path'] = folder_path
        
        return self._request('GET', f'/{bucket}/files', params=params)
    
    def get_download_url(self, bucket: str, key: str) -> str:
        """
        Get pre-signed download URL.
        
        Args:
            bucket: Bucket name
            key: File key (path)
            
        Returns:
            Download URL (valid for 60 minutes)
        """
        response = self._request('GET', f'/{bucket}/download/{key}')
        return response.get('download_url', '')
    
    def download_file(
        self,
        bucket: str,
        key: str,
        local_path: Union[str, Path]
    ) -> None:
        """
        Download file to local path.
        
        Args:
            bucket: Bucket name
            key: File key
            local_path: Local destination path
        """
        url = self.get_download_url(bucket, key)
        
        response = requests.get(url, stream=True, timeout=self.timeout)
        response.raise_for_status()
        
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def get_file_info(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            bucket: Bucket name
            key: File key
            
        Returns:
            File info
        """
        response = self._request('GET', f'/{bucket}/file-info/{key}')
        return response.get('file', {})
    
    def delete_file(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            bucket: Bucket name
            key: File key
            
        Returns:
            Response data
        """
        return self._request('DELETE', f'/{bucket}/file/{key}')
    
    # ==================== Permissions ====================
    
    def add_permission(
        self,
        bucket: str,
        target_type: str,
        target_id: str,
        resource_type: str,
        resource_path: str,
        can_read: bool = False,
        can_write: bool = False,
        can_delete: bool = False,
        can_list: bool = False
    ) -> Dict[str, Any]:
        """
        Add bucket permission.
        
        Args:
            bucket: Bucket name
            target_type: 'user' or 'workspace'
            target_id: User/workspace ID
            resource_type: 'bucket' or 'folder'
            resource_path: Path to resource
            can_read: Read permission
            can_write: Write permission
            can_delete: Delete permission
            can_list: List permission
            
        Returns:
            Permission info
        """
        payload = {
            'target_type': target_type,
            'target_id': target_id,
            'resource_type': resource_type,
            'resource_path': resource_path,
            'can_read': can_read,
            'can_write': can_write,
            'can_delete': can_delete,
            'can_list': can_list
        }
        response = self._request('POST', f'/{bucket}/permission/add', json_data=payload)
        return response.get('permission', {})
    
    def list_permissions(self, bucket: str) -> List[Dict[str, Any]]:
        """
        List bucket permissions.
        
        Args:
            bucket: Bucket name
            
        Returns:
            List of permissions
        """
        response = self._request('GET', f'/{bucket}/permissions')
        return response.get('permissions', [])
    
    def delete_permission(self, permission_id: str) -> Dict[str, Any]:
        """
        Delete a permission.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            Response data
        """
        return self._request('DELETE', f'/permission/{permission_id}')
    
    # ==================== Utilities ====================
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage stats
        """
        response = self._request('GET', '/stats')
        return response.get('stats', {})


__all__ = ['LexiaStorage', 'LexiaStorageException']

