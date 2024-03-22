import os
import tarfile
from pathlib import Path
from google.cloud import storage


def get_file(bucket_name, blob_name, dest_dir):
    print(f"Downloading file {bucket_name}/{blob_name}")

    project_number = os.environ.get("CLOUD_ML_PROJECT_ID")
    storage_client = storage.Client(project=project_number) if project_number is not None else storage.Client()
    print("   Storage client created")

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(f"{blob_name}")
    local_archive = os.path.join(dest_dir, "data.tar.gz")

    print("   Starting download")
    blob.download_to_filename(local_archive)

    print(f"   Downloaded storage object from bucket {bucket_name} to local directory {dest_dir}")
    archive_dir = os.path.join(dest_dir, Path(blob_name).stem)

    with tarfile.open(local_archive, "r") as tf:
        tf.extractall(path=archive_dir)

    os.remove(local_archive)

    print(f"   All files extracted to {archive_dir}")
    return archive_dir


def get_model(bucket_name, blob_name, dest_dir):
    print(f"Downloading storage object {blob_name} from bucket {bucket_name}")

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(f"{blob_name}")
    local_archive = os.path.join(dest_dir, "model.h5")
    blob.download_to_filename(local_archive)

    print(f"   Downloaded storage object from bucket {bucket_name} to local file {dest_dir}")

    return local_archive


def save_file(file_path, bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    print(f"File {file_path} exported to bucket {bucket_name} as {blob_name}")
