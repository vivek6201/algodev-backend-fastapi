import typing
from datetime import datetime, timedelta
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from app.common.lib.formatter import FileResponse
from app.config.settings import settings


def _load_cloudfront_private_key_from_file(private_key_path: str):
    """Loads the CloudFront private key from a PEM file path."""
    try:
        file_path = Path(private_key_path)
        if not file_path.is_absolute():
            root_path = Path(__file__).resolve().parent.parent.parent.parent.parent
            file_path = root_path / private_key_path

        if not file_path.exists():
            print(f"Error: CloudFront private key file not found at {file_path}")
            return None

        with open(file_path, "rb") as key_file:
            private_key_bytes = key_file.read()
        return load_pem_private_key(private_key_bytes, password=None, backend=default_backend())
    except FileNotFoundError:
        print(f"Error: CloudFront private key file not found at {private_key_path}")
        return None
    except Exception as e:
        print(f"Error loading CloudFront private key from file: {e}")
        return None


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
        self.cloudfront_key_id = settings.AWS_CLOUDFRONT_KEYPAIR_ID

        # Load key from settings if present (preferred), or file fallback
        key_content = settings.AWS_CLOUDFRONT_PRIVATE_KEY
        if key_content:
            key_bytes = key_content.encode("utf-8")
            self.cloudfront_private_key = load_pem_private_key(
                key_bytes, password=None, backend=default_backend()
            )
        else:
            self.cloudfront_private_key = _load_cloudfront_private_key_from_file(
                private_key_path="cloudfront_private_key.pem"
            )

    def upload_file(
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
            self.s3_client.upload_fileobj(
                file_obj, self.bucket_name, object_name, ExtraArgs=extra_args
            )
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None
        return object_name

    def delete_file(self, object_name: str) -> bool:
        """Delete a file from an S3 bucket

        :param object_name: S3 object name to delete
        :return: True if file was deleted, else False
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
        return True

    def get_file(self, object_name: str) -> typing.Optional[dict]:
        """Get file metadata and signed URL from S3

        :param object_name: S3 object name
        :return: Dictionary with url, type, extension, size, etc.
        """
        try:
            head_response = self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)

            url = self.get_signed_url(object_name)

            file_extension = Path(object_name).suffix.lower().lstrip(".")

            return FileResponse(
                url=url,
                type=head_response.get("ContentType"),
                extension=file_extension,
                size=head_response.get("ContentLength"),
                last_modified=head_response.get("LastModified"),
            )
        except ClientError as e:
            # If the file doesn't exist or other S3 error
            print(f"Error getting file info from S3: {e}")
            return None

    def get_signed_url(self, object_name: str, expiration: int = 3600) -> str:
        """Generate a presigned URL to share an S3 object

        :param object_name: S3 object name
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        # If CloudFront is configured, return CloudFront signed URL
        if self.cloudfront_domain and self.cloudfront_key_id and self.cloudfront_private_key:
            return self._get_cloudfront_signed_url(object_name, expiration)

        # Fallback to S3 presigned URL
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

        return response

    def _rsa_signer(self, message):
        """Callback for CloudFrontSigner to sign bytes using the private key."""
        return self.cloudfront_private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

    def _get_cloudfront_signed_url(self, object_name: str, expiration: int) -> str:
        """Generate a signed URL for CloudFront using botocore signer"""
        url = f"https://{self.cloudfront_domain}/{object_name}"
        expires = datetime.utcnow() + timedelta(seconds=expiration)

        try:
            cloudfront_signer = CloudFrontSigner(self.cloudfront_key_id, self._rsa_signer)
            signed_url = cloudfront_signer.generate_presigned_url(url, date_less_than=expires)
            return signed_url
        except Exception as e:
            print(f"Error signing CloudFront URL: {e}")
            return None
