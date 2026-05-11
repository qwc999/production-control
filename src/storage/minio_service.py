from datetime import timedelta

from minio import Minio

from src.core.config import settings


class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )

    def ensure_bucket(self, bucket_name: str) -> None:
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_file(
            self,
            bucket_name: str,
            file_path: str,
            object_name: str,
            expires_days: int = 7
    ) -> str:
        self.ensure_bucket(bucket_name)

        self.client.fput_object(
            bucket_name=bucket_name,
            file_path=file_path,
            object_name=object_name
        )

        return self.client.presigned_get_object(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=expires_days)
        )
