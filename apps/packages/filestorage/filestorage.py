import io
import uuid

from minio import Minio

from .config import config

client = Minio(
    config.minio_endpoint,
    access_key=config.minio_access_key,
    secret_key=config.minio_secret_key,
    secure=False,
)


def upload(file: bytes, bucket_name: str = "excel") -> str:
    """
    Uploads a file to the MinIO bucket

    :param file: The file to upload
    :return: The UUID of the file
    """

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)

    minio_uuid = str(uuid.uuid4())
    client.put_object(
        bucket_name,
        minio_uuid,
        io.BytesIO(file),
        len(file),
    )

    return minio_uuid


def download(minio_uuid: str, bucket_name: str = "excel") -> bytes:
    """
    Downloads a file from the MinIO bucket

    :param minio_uuid: The UUID of the file
    :return: The file
    """

    return client.get_object(bucket_name, minio_uuid).read()


def delete(minio_uuid: str, bucket_name: str = "excel"):
    """
    Deletes a file from the MinIO bucket

    :param minio_uuid: The UUID of the file
    """

    client.remove_object(bucket_name, minio_uuid)


def get_url(minio_uuid: str, bucket_name: str = "excel") -> str:
    """
    Gets the URL of the file

    :param minio_uuid: The UUID of the file
    :return: The URL
    """

    return (
        "https://nekoparser-s3.dan.tatar/"
        + client.presigned_get_object(bucket_name, minio_uuid).split("/", maxsplit=3)[-1]
    )
