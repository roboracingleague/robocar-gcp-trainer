import os
import tarfile
from pathlib import Path
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

def get_archive(bucket_name, blob_name, dest_dir):
    logger.info(f"Downloading file {bucket_name}/{blob_name}")

    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()
    logger.debug("Storage client created")

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(blob_name)
    local_archive = os.path.join(dest_dir, "data.tar.gz")

    logger.debug("Starting download")
    blob.download_to_filename(local_archive)

    logger.debug(f"Downloaded storage object from bucket {bucket_name} to local directory {dest_dir}")

    with tarfile.open(local_archive, "r") as tf:
        tf.extractall(path=dest_dir)

    os.remove(local_archive)

    archive_dir = os.path.join(dest_dir, Path(blob_name).stem)
    logger.info(f"Files extracted to {archive_dir}")
    return archive_dir


def get_model(bucket_name, blob_name, dest_dir):
    logger.info(f"Downloading storage object {blob_name} from bucket {bucket_name}")

    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(blob_name)
    local_archive = os.path.join(dest_dir, "model")
    blob.download_to_filename(local_archive)

    logger.info(f"Storage object {blob_name} from bucket {bucket_name} downloaded to local file {local_archive}")
    return local_archive


def save_file(file_path, bucket_name, blob_name):
    logger.info(f"Exporting file {file_path} to bucket {bucket_name} as {blob_name}")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_filename(file_path, if_generation_match=0)

    logger.info(f"File {file_path} exported to bucket {bucket_name} as {blob_name}")
