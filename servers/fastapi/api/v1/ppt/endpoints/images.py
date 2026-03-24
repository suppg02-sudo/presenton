import os
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....database import get_async_session
from ....models.sql.image_asset import ImageAsset

# Create router
IMAGES_ROUTER = APIRouter(prefix="/images", tags=["images"])

# Configuration
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "public" / "images" / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@IMAGES_ROUTER.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    presentation_id: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Upload an image file for use in presentations.
    
    Args:
        file: Image file (JPEG, PNG, WebP, max 5MB)
        presentation_id: Optional presentation ID to associate image
        session: Database session
    
    Returns:
        ImageAsset object with public URL
    """
    try:
        # Validate file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read and validate file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: 5MB"
            )
        
        # Determine MIME type
        mime_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp"
        }
        mime_type = mime_types.get(file_ext, "application/octet-stream")
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        new_filename = f"{unique_id}.{file_ext}"
        file_path = UPLOAD_DIR / new_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Create database record
        image_asset = ImageAsset(
            id=unique_id,
            presentation_id=presentation_id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(file_content),
            mime_type=mime_type,
            url=f"/images/uploads/{new_filename}",
            uploaded_at=datetime.now()
        )
        
        session.add(image_asset)
        await session.commit()
        await session.refresh(image_asset)
        
        return {
            "success": True,
            "image_id": image_asset.id,
            "file_name": image_asset.file_name,
            "url": image_asset.url,
            "file_size": image_asset.file_size,
            "mime_type": image_asset.mime_type,
            "message": "Image uploaded successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading image: {str(e)}"
        )


@IMAGES_ROUTER.get("/list")
async def list_images(
    presentation_id: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """
    List uploaded images, optionally filtered by presentation.
    
    Args:
        presentation_id: Optional presentation ID to filter by
        session: Database session
    
    Returns:
        List of ImageAsset objects
    """
    try:
        if presentation_id:
            stmt = select(ImageAsset).where(ImageAsset.presentation_id == presentation_id)
        else:
            stmt = select(ImageAsset)
        
        result = await session.execute(stmt)
        images = result.scalars().all()
        
        return {
            "success": True,
            "count": len(images),
            "images": [
                {
                    "id": img.id,
                    "file_name": img.file_name,
                    "url": img.url,
                    "file_size": img.file_size,
                    "mime_type": img.mime_type,
                    "uploaded_at": img.uploaded_at,
                    "presentation_id": img.presentation_id
                }
                for img in images
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing images: {str(e)}"
        )


@IMAGES_ROUTER.delete("/{image_id}")
async def delete_image(
    image_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete an uploaded image.
    
    Args:
        image_id: Image ID to delete
        session: Database session
    
    Returns:
        Success message
    """
    try:
        # Find image
        stmt = select(ImageAsset).where(ImageAsset.id == image_id)
        result = await session.execute(stmt)
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete file
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
        
        # Delete database record
        await session.delete(image)
        await session.commit()
        
        return {
            "success": True,
            "message": f"Image {image_id} deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting image: {str(e)}"
        )


@IMAGES_ROUTER.get("/pptx-assets")
async def get_pptx_assets():
    """
    Get list of pre-extracted PPTX background images.
    
    Returns:
        List of available PPTX assets
    """
    assets_dir = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "public" / "images" / "usdaw-template"
    
    assets = []
    if assets_dir.exists():
        for file in assets_dir.glob("*"):
            if file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                assets.append({
                    "id": file.stem,
                    "name": file.stem.replace("-", " ").title(),
                    "url": f"/images/usdaw-template/{file.name}",
                    "file_size": file.stat().st_size
                })
    
    return {
        "success": True,
        "count": len(assets),
        "assets": assets
    }

