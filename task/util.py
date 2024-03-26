import os
import tarfile
from pathlib import Path
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

def download_file(bucket_name, blob_name, dest_path):
    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()
    logger.debug("Storage client created")
    bucket = storage_client.bucket(bucket_name)
    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(blob_name)
    blob.download_to_filename(dest_path)
    logger.debug(f"Archive downloaded to {dest_path}")

def upload_file(file_path, bucket_name, blob_name):
    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)

def tar(file_path, archive_path):
    logger.debug(f"Tar {file_path} to {archive_path}")
    with tarfile.open(archive_path, 'w:gz') as archive:
        arcname = os.path.split(file_path)[1]
        archive.add(file_path, arcname=arcname)

def untar(archive_path, dest_path):
    logger.debug(f"Untar {archive_path} to {dest_path}")
    with tarfile.open(archive_path, "r") as tf:
        tf.extractall(path=dest_path)
    os.remove(archive_path)

def get_archive(bucket_name, blob_name, dest_dir):
    logger.info(f"Downloading {bucket_name}/{blob_name}")
    local_archive = os.path.join(dest_dir, 'archive.tgz')
    download_file(bucket_name, blob_name, local_archive)
    untar(local_archive, dest_dir)

def save_to_archive(path, bucket_name, blob_name):
    logger.info(f"Uploading {path} to {bucket_name}/{blob_name}")
    local_archive = 'archive.tgz'
    tar(path, local_archive)
    upload_file(local_archive, bucket_name, blob_name)
    os.remove(local_archive)
