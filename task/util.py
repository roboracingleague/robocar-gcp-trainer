import os
import tempfile
import tarfile

from google.cloud import storage

DATA_DIR = tempfile.TemporaryDirectory(suffix=None, prefix='steering_training')

def get_archive (bucket_name, url):

    print(f"Downloading storage object training/{url} from bucket {bucket_name}")

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(f"training/{url}")
    local_archive=os.path.join(DATA_DIR.name,"data.tar.gz")
    blob.download_to_filename(local_archive)

    print(
        "Downloaded storage object from bucket {} to local file {}.".format(
            bucket_name, DATA_DIR.name
        )
    )

    with tarfile.open(local_archive, "r") as tf:
        tf.extractall(path=DATA_DIR.name)
    print("All files extracted")


    return DATA_DIR.name

def get_model (bucket_name, url):

    print(f"Downloading storage object models/{url} from bucket {bucket_name}")

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(f"models/{url}")
    local_archive=os.path.join(DATA_DIR.name,"model.h5")
    blob.download_to_filename(local_archive)

    print(
        "Downloaded storage object from bucket {} to local file {}.".format(
            bucket_name, DATA_DIR.name
        )
    )

    return DATA_DIR.name

def save_model (bucket, filepath, src_filename, dst_filename):

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket)

    gcs_object = bucket.blob(os.path.join('models',dst_filename))
    gcs_object.upload_from_filename(os.path.join(filepath,src_filename))

def save_movie (bucket, filepath, src_filename, dst_filename):

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket)

    gcs_object = bucket.blob(os.path.join('movies',dst_filename))
    gcs_object.upload_from_filename(os.path.join(filepath,src_filename))
