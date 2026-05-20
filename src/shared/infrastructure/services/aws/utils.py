from typing import cast
from types_aiobotocore_s3.literals import BucketLocationConstraintType
from types_aiobotocore_cloudfront import CloudFrontClient
from types_aiobotocore_iam import IAMClient
from types_aiobotocore_s3 import S3Client
from src.core.config import settings
from botocore.exceptions import ClientError
from botocore.signers import CloudFrontSigner
from datetime import datetime, timedelta, UTC
import rsa
import logging
import json


PUBLIC_READ_POLICY = {
    "version": "2012-10-17",
    "statement": [
        {
            "effect": "Allow",
            "principal": "*",
            "action": "s3:GetObject",
            "resource": f"arn:aws:s3:::{settings.aws_s3_bucket_name}/*",
        }
    ],
}

PRIVATE_WRITE_POLICY = {
    "version": "2012-10-17",
    "statement": [
        {
            "effect": "Allow",
            "action": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject"],
            "resource": f"arn:aws:s3:::{settings.aws_s3_bucket_name}/*",
        }
    ],
}


def invalidate_cache(client: CloudFrontClient, key: str):
    return client.create_invalidation(
        DistributionId=settings.aws_distribution_id,
        InvalidationBatch={
            "Paths": {"Quantity": 1, "Items": [f"/{key}"]},
            "CallerReference": key,
        },
    )


def generate_object_url(key: str) -> str:
    return f"https://{settings.aws_s3_bucket_name}.s3.{settings.aws_s3_region}.amazonaws.com/{key}"


def rsa_signer(message):
    private_key_str = settings.cloudfront_private_key.get_secret_value()
    private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
    return rsa.sign(message, private_key, "SHA-1")


def signed_url(url: str):
    cloudfront_signer = CloudFrontSigner(settings.cloudfront_key_pair_id, rsa_signer)

    return cloudfront_signer.generate_presigned_url(
        url, date_less_than=datetime.now(UTC) + timedelta(days=1)
    )


async def set_iam_policy(client: IAMClient, policy: dict):
    """Set IAM policy to allow access to the S3 bucket.
    Args:
        client: The IAM client to use for setting the IAM policy.
        policy: The IAM policy to set, defined as a dictionary."""
    try:
        POLICY_NAME = f"S3{settings.aws_s3_bucket_name}Access"
        ROLE_NAME = "S3AccessRole"
        ACCOUNT_ID = (
            settings.aws_s3_account_id.get_secret_value()
            if settings.aws_s3_account_id
            else None
        )

        await client.put_role_policy(
            RoleName=ROLE_NAME,
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy),
        )

        await client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=f"arn:aws:iam::{ACCOUNT_ID}:policy/{POLICY_NAME}",
        )

    except ClientError as error:
        logging.error(f"Error setting IAM policy: {error}")


async def create_bucket(bucket_name: str, client: S3Client):
    """Create an S3 bucket with the specified name and region.
    Args:
        bucket_name: The name of the S3 bucket to create.
        client: The S3 client to use for creating the bucket.
    """
    try:
        await client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": cast(
                    BucketLocationConstraintType, settings.aws_s3_region
                ),
                "Location": {"Type": "AvailabilityZone", "Name": "eu-north-1a"},
                "Bucket": {
                    "DataRedundancy": "SingleAvailabilityZone",
                    "Type": "Directory",
                },
            },
            ObjectOwnership="BucketOwnerEnforced",
        )

        await set_public_access(client, bucket_name)
    except client.exceptions.BucketAlreadyExists as error:
        logging.error(f"Bucket already exists: {error}")
    except client.exceptions.BucketAlreadyOwnedByYou as error:
        logging.error(f"Bucket already owned by you: {error}")
    except ClientError as error:
        logging.error(f"Error creating bucket: {error}")


async def set_bucket_policy(client: S3Client, bucket_name: str, policy: dict):
    """Set bucket policy to allow public read access.
    Args:
        client: The S3 client to use for setting the bucket policy.
        bucket_name: The name of the S3 bucket for which to set the policy.
        policy: The bucket policy to set, defined as a dictionary."""
    try:
        await client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
    except ClientError as error:
        logging.error(f"Error setting bucket policy: {error}")


async def set_public_access(client: S3Client, bucket_name: str):
    """Set public access block for the bucket.
    Args:
        client: The S3 client to use for setting the public access block.
        bucket_name: The name of the S3 bucket for which to set the public access block.
    """
    try:
        await client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False,
            },
        )
    except ClientError as error:
        logging.error(f"Error setting public access: {error}")


async def bucket_exists(client: S3Client, bucket_name: str) -> bool:
    """Check if an S3 bucket exists.
    Args:
        client: The S3 client to use for checking the bucket existence.
        bucket_name: The name of the S3 bucket to check for existence.
    Returns:
        bool: True if the bucket exists, False otherwise."""
    try:
        await client.head_bucket(Bucket=bucket_name)
        return True
    except client.exceptions.NoSuchBucket as error:
        return False


async def generate_presigned_url(
    client: S3Client, bucket_name: str, object_key: str
) -> str:
    """Generate a presigned URL for an S3 object.
    Args:
        client: The S3 client to use for generating the presigned URL.
        bucket_name: The name of the S3 bucket containing the object.
        object_key: The key of the S3 object for which to generate the presigned URL.
        Returns:
            str: The generated presigned URL."""

    return await client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": bucket_name,
            "Key": object_key,
        },
        ExpiresIn=500,
    )
