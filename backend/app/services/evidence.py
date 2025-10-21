import base64
import hashlib
from pathlib import Path
from typing import Dict, Tuple

from app.core.config import settings
from app.services.s3 import s3_service


async def save_evidence_file_streaming(file_stream, filename: str, org_id: int, system_id: int, file_size: int) -> Tuple[str, str]:
    """
    Save uploaded evidence file using streaming and generate checksum.

    Args:
        file_stream: File stream/chunks
        filename: Name of the file
        org_id: Organization ID
        system_id: AI System ID
        file_size: Total file size in bytes

    Returns:
        Tuple of (file_path, checksum)
    """
    # Initialize SHA256 hasher
    hasher = hashlib.sha256()

    if settings.use_s3:
        # S3/R2 storage path
        s3_key = f"evidence/org_{org_id}/system_{system_id}/{filename}"
        
        # For S3, we return the key as the "path" and let the client upload directly
        # via presigned URL (handled in the endpoint)
        # Note: In a real S3 implementation, you'd stream directly to S3
        return s3_key, "placeholder_checksum"
    else:
        # Local file storage (DEV mode) with streaming
        evidence_dir = Path(f"./evidence/org_{org_id}/system_{system_id}")
        evidence_dir.mkdir(parents=True, exist_ok=True)

        file_path = evidence_dir / filename
        with open(file_path, "wb") as f:
            # Stream file content and calculate checksum
            for chunk in file_stream:
                f.write(chunk)
                hasher.update(chunk)

        checksum = hasher.hexdigest()
        return str(file_path), checksum


def get_evidence_upload_info(file_name: str, org_id: int, system_id: int, checksum: str) -> Dict[str, str]:
    """
    Get upload information for evidence file.

    For S3: Returns presigned URL for client-side upload
    For local: Returns None (server handles upload)

    Args:
        file_name: Name of file to upload
        org_id: Organization ID
        system_id: AI System ID
        checksum: SHA-256 checksum (hex)

    Returns:
        Dict with upload_url (if S3) and file_path
    """
    if settings.use_s3:
        s3_key = f"evidence/org_{org_id}/system_{system_id}/{file_name}"
        
        # Convert hex checksum to base64 for S3
        checksum_bytes = bytes.fromhex(checksum)
        checksum_b64 = base64.b64encode(checksum_bytes).decode()
        
        presigned_url = s3_service.generate_presigned_url(
            key=s3_key,
            expires_in=3600,  # 1 hour
            checksum_sha256=checksum_b64,
        )
        
        return {
            "upload_url": presigned_url,
            "file_path": s3_key,
            "method": "PUT",
            "checksum_header": f"x-amz-checksum-sha256: {checksum_b64}",
        }
    else:
        return {
            "file_path": f"evidence/org_{org_id}/system_{system_id}/{file_name}",
            "method": "POST",
        }

