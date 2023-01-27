import os
import tempfile
import tarfile

from google.cloud import storage

DATA_DIR = tempfile.TemporaryDirectory(suffix=None, prefix='steering_training')
BUCKET_NAME = "steering-model"

def get_archive (url):

    print(
        "Downloading storage object {}.".format(
            url
        )
    )

    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(f"training/{url}")
    local_archive=os.path.join(DATA_DIR.name,"data.tar.gz")
    blob.download_to_filename(local_archive)

    print(
        "Downloaded storage object from bucket {} to local file {}.".format(
            BUCKET_NAME, DATA_DIR.name
        )
    )

    with tarfile.open(local_archive, "r") as tf:
        tf.extractall(path=DATA_DIR.name)
    print("All files extracted")


    return DATA_DIR.name

def save_model (filepath, src_filename, dst_filename):

    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)

    gcs_object = bucket.blob(os.path.join('models',dst_filename))
    gcs_object.upload_from_filename(os.path.join(filepath,src_filename))
