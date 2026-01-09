"""File handling utilities for uploads."""
import os
import uuid
import shutil
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from pathlib import Path

from ..config import settings


class FileHandler:
    """Handle file uploads and storage."""
    
    ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mpeg", ".mov", ".avi"}
    
    def __init__(self, upload_dir: Optional[str] = None):
        """Initialize file handler with upload directory."""
        self.upload_dir = Path(upload_dir or settings.UPLOAD_DIR)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.upload_dir,
            self.upload_dir / "images",
            self.upload_dir / "videos",
            self.upload_dir / "temp"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file: UploadFile, file_type: str = "image") -> Tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file
            file_type: Expected file type ('image' or 'video')
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not file.filename:
            return False, "No filename provided"
        
        # Get file extension
        ext = Path(file.filename).suffix.lower()
        
        if file_type == "image":
            if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
                return False, f"Invalid image format. Allowed: {', '.join(self.ALLOWED_IMAGE_EXTENSIONS)}"
            if file.content_type and file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                return False, f"Invalid content type: {file.content_type}"
        elif file_type == "video":
            if ext not in self.ALLOWED_VIDEO_EXTENSIONS:
                return False, f"Invalid video format. Allowed: {', '.join(self.ALLOWED_VIDEO_EXTENSIONS)}"
            if file.content_type and file.content_type not in settings.ALLOWED_VIDEO_TYPES:
                return False, f"Invalid content type: {file.content_type}"
        else:
            return False, f"Unknown file type: {file_type}"
        
        return True, "Valid"
    
    async def save_upload(
        self,
        file: UploadFile,
        file_type: str = "image",
        subfolder: Optional[str] = None
    ) -> dict:
        """
        Save uploaded file to storage.
        
        Args:
            file: Uploaded file
            file_type: Type of file ('image' or 'video')
            subfolder: Optional subfolder within type directory
            
        Returns:
            Dict with file info including path
        """
        # Validate file
        is_valid, message = self.validate_file(file, file_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Generate unique filename
        ext = Path(file.filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{timestamp}_{unique_id}{ext}"
        
        # Determine save path
        type_dir = "images" if file_type == "image" else "videos"
        if subfolder:
            save_dir = self.upload_dir / type_dir / subfolder
        else:
            save_dir = self.upload_dir / type_dir
        
        save_dir.mkdir(parents=True, exist_ok=True)
        file_path = save_dir / new_filename
        
        # Save file
        try:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        return {
            "filename": new_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.upload_dir)),
            "file_type": file_type,
            "file_size": len(content),
            "content_type": file.content_type,
            "upload_time": datetime.utcnow()
        }
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_path(self, relative_path: str) -> Optional[Path]:
        """
        Get full file path from relative path.
        
        Args:
            relative_path: Relative path within upload directory
            
        Returns:
            Full path if exists, None otherwise
        """
        full_path = self.upload_dir / relative_path
        if full_path.exists():
            return full_path
        return None
    
    def list_files(self, file_type: str = "image", subfolder: Optional[str] = None) -> list:
        """
        List files in storage.
        
        Args:
            file_type: Type of files to list
            subfolder: Optional subfolder
            
        Returns:
            List of file info dicts
        """
        type_dir = "images" if file_type == "image" else "videos"
        search_dir = self.upload_dir / type_dir
        if subfolder:
            search_dir = search_dir / subfolder
        
        if not search_dir.exists():
            return []
        
        files = []
        extensions = self.ALLOWED_IMAGE_EXTENSIONS if file_type == "image" else self.ALLOWED_VIDEO_EXTENSIONS
        
        for file_path in search_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)


# Default file handler instance
file_handler = FileHandler()
