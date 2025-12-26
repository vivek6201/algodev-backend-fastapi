import typing
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from starlette.concurrency import run_in_threadpool

from app.common.lib.formatter import FileResponse
from app.config.settings import settings


class S3Service:
    def __init__(self):
        self.s3_client: boto3.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET
        self.cloudfront_domain = settings.AWS_CLOUDFRONT_DOMAIN

    async def upload_file(
        self, file_obj: typing.IO, object_name: str, content_type: str = None
    ) -> typing.Optional[str]:
        """Upload a file to an S3 bucket

        :param file_obj: File to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :param content_type: Content-Type of the file
        :return: Object name if file was uploaded, else None
        """
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:

            def _upload():
                self.s3_client.upload_fileobj(
                    file_obj, self.bucket_name, object_name, ExtraArgs=extra_args
                )

            await run_in_threadpool(_upload)
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None
        return object_name

    async def delete_file(self, object_name: str) -> bool:
        """Delete a file from an S3 bucket

        :param object_name: S3 object name to delete
        :return: True if file was deleted, else False
        """
        try:

            def _delete():
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)

            await run_in_threadpool(_delete)
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
        return True

    async def get_file(self, object_name: str) -> typing.Optional[dict]:
        """Get file metadata and URL from S3

        :param object_name: S3 object name
        :return: Dictionary with url, type, extension, size, etc.
        """
        try:

            def _head():
                return self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)

            head_response = await run_in_threadpool(_head)

            url = self.get_url(object_name)

            file_extension = Path(object_name).suffix.lower().lstrip(".")

            return FileResponse(
                url=url,
                type=head_response.get("ContentType"),
                extension=file_extension,
                size=head_response.get("ContentLength"),
                last_modified=head_response.get("LastModified"),
                id=object_name,
            )
        except ClientError as e:
            # If the file doesn't exist or other S3 error
            print(f"Error getting file info from S3: {e}")
            return None

    def get_url(self, object_name: str) -> str:
        """Generate a CloudFront URL for an S3 object (unsigned, no expiration)

        :param object_name: S3 object name
        :return: CloudFront URL as string
        """
        return f"https://{self.cloudfront_domain}/{object_name}"
