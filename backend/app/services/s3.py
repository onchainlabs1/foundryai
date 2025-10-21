"""S3/R2 storage service for evidence files."""

from typing import Optional

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings


class S3Service:
    """Service for S3/R2 file operations."""

    def __init__(self):
        """Initialize S3 client if configured."""
        self.client = None
        if settings.use_s3:
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=BotoConfig(
                    s3={"addressing_style": "path" if settings.S3_FORCE_PATH_STYLE else "auto"}
                ),
            )

    def generate_presigned_url(
        self, key: str, expires_in: int = 3600, checksum_sha256: Optional[str] = None
    ) -> str:
        """
        Generate presigned URL for PUT upload.

        Args:
            key: S3 object key
            expires_in: URL expiration in seconds
            checksum_sha256: Expected SHA-256 checksum (base64)

        Returns:
            Presigned URL for PUT upload
        """
        if not self.client:
            raise ValueError("S3 client not configured")

        params = {
            "Bucket": settings.S3_BUCKET,
            "Key": key,
        }

        if checksum_sha256:
            params["ChecksumSHA256"] = checksum_sha256

        return self.client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=expires_in,
        )

    def generate_presigned_get_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for GET download/viewing.

        Args:
            key: S3 object key
            expires_in: URL expiration in seconds

        Returns:
            Presigned URL for GET download
        """
        if not self.client:
            raise ValueError("S3 client not configured")

        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )

    def check_file_exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        if not self.client:
            return False

        try:
            self.client.head_object(Bucket=settings.S3_BUCKET, Key=key)
            return True
        except ClientError:
            return False

    def get_file_checksum(self, key: str) -> Optional[str]:
        """Get SHA-256 checksum of S3 object."""
        if not self.client:
            return None

        try:
            response = self.client.head_object(Bucket=settings.S3_BUCKET, Key=key)
            # R2/S3 stores checksum in metadata or ETag
            return response.get("ChecksumSHA256") or response.get("ETag", "").strip('"')
        except ClientError:
            return None

    def delete_file(self, key: str) -> bool:
        """Delete file from S3."""
        if not self.client:
            return False

        try:
            self.client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
            return True
        except ClientError:
            return False

    def health_check(self) -> bool:
        """Check S3 connectivity."""
        if not self.client:
            return False

        try:
            self.client.head_bucket(Bucket=settings.S3_BUCKET)
            return True
        except ClientError:
            return False


# Global S3 service instance
s3_service = S3Service()

