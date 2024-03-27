# Robocar GCP Trainer

## Purpose

Train your model using google Vertex AI service (not free, arround 0.2€ per training on the basic keras linear model).
For 13k images, Training duration is about 13mins (9min to start the process, then 4 mins to unpack dataset, tain model and convert to tflite).

Beyond using cloud to train model, idea here is to rely on donkeycar source code for the training so that training your model using donkey cli, donkey ui, or this method, is the same, has the same level of features and works the same way.

## Requirement

- have docker
- install gcloud CLI
- have a GCP account with roles to create a Vertex AI job and push/pull images inartefact registry
- create a project with billing activated
- create a bucket (used for storage of dataset, job temporary files and model created)
- make sure following env variable are defined :
  - (optionnal is service account is used) GOOGLE_APPLICATION_CREDENTIALS, or (if service account not used) follow https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=fr#how-to

```bash
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json

export REGION="europe-west1"
export BUCKET_NAME="irn-71028-dvc-lab-robocars-datasets"
export JOB_PREFIX="pc91"

export PROJECT_ID='irn-71028-lab-a6'
export REPO_NAME=robocar
export IMAGE_NAME=robocar-gcp-trainer
export IMAGE_TAG=latest
export IMAGE_URI=europe-west1-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}

export DOCKER_GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/application_default_credentials.json
export CLOUD_ML_PROJECT_ID=$PROJECT_ID
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
```

## Vertex AI usage

### gcloud login

Login to gcloud as follow to submit Vertex AI jobs and push images :

```bash
gcloud auth login
```

Login application to gcloud as follow to run docker locally :

```bash
gcloud auth application-default login
```

You may need to configure docker repo :

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

### Build and push Docker image

```bash
docker build -f Dockerfile -t "${IMAGE_URI}" .
docker push ${IMAGE_URI}
```

### Run job

Set parameters :

```bash
export MODEL_TYPE=behavior
export MODEL=models/model_name.savedmodel
export ARCHIVES='dataset-specialized-training/data-20240126164806-20240219204548-behav-C.tgz'

export TRANSFER=models/model_name.savedmodel.tgz
export CONFIG=configs/config.tgz
```

- TRANSFER and CONFIG are optionals. Template 'cfg_complete.py' is used as default config if not given.
- MODEL ARCHIVES TRANSFER and CONFIG are GCS blob names within BUCKET_NAME GCS bucket.
- To use multiple blobs for ARCHIVES, separate them with ':' (coma is already used by google)

Run locally :

```bash
docker run -e GOOGLE_CLOUD_PROJECT -e CLOUD_ML_PROJECT_ID -e GOOGLE_APPLICATION_CREDENTIALS="${DOCKER_GOOGLE_APPLICATION_CREDENTIALS}" -v ${GOOGLE_APPLICATION_CREDENTIALS}:${DOCKER_GOOGLE_APPLICATION_CREDENTIALS}:ro "${IMAGE_URI}" --bucket "$BUCKET_NAME" --archives "$ARCHIVES" --type "${MODEL_TYPE}" --model ${MODEL} --config "${CONFIG}" --transfer "${TRANSFER}"
```

Run with Vertex AI :

```bash
gcloud ai custom-jobs create --region="${REGION}" --config=config.yaml --args=--bucket="${BUCKET_NAME}" --args=--archives="${ARCHIVES}" --args=--type="${MODEL_TYPE}" --display-name="${JOB_PREFIX}-robocar-train" --args=--model="${MODEL}" --args=--transfer="${TRANSFER}" --args=--config="${CONFIG}"
```

May be usefull to debug :

```bash
docker run -e CLOUD_ML_PROJECT_ID -e GOOGLE_APPLICATION_CREDENTIALS="${DOCKER_GOOGLE_APPLICATION_CREDENTIALS}" -v ${LOCAL_GOOGLE_APPLICATION_CREDENTIALS}:${GOOGLE_APPLICATION_CREDENTIALS}:ro -it --entrypoint=/bin/bash "${IMAGE_URI}" -i
```

## Scripts usage

All steps of training including dataset handling can be done through provided scripts.
All scripts have a default functionnal behavior, to get help, invoaue script with ```-h```

### Create dataset archive

use the ```make_tub_archive.sh``` script, from your 'car' directory

you must call this script from your "car" directory. The script will automatically include config.py and myconfig.py to your dataset, so that training will be based on it.

usage :

```bash
./make_tub_archive.sh [-t <tub directory>] [-a <archive basename>] [-h]
```

Default tub directory is ```data```.
Default archive basename is ```wip```.

For example, to specify another tub directory or subdirectory :

```bash
./make_tub_archive.sh -t data/steering_data
```

### Upload archive to your GCS bucket

use the ```upload_tub_archive.sh``` script

The script will upload archive to subdirectory training

usage :

```bash
./upload_tub_archive.sh [-a <archive name>]
```

Default archive name is ```wip.tgz```.

### Start local training (usefull at least to check that everything is fine)

```bash
./local_train.sh [-a <archive name>]
```

Default archive name is ```wip.tgz```.

### Start training using google ai-platform

```bash
./submit_cloud_train.sh [-a <archive name>]
```

Default archive name is ```wip.tgz```.

### Start local salient makemovie (usefull at least to check that everything is fine)

```bash
./local_makemovie.sh [-m <model.h5>] [-a <archive name>] 
```

Default archive name is ```wip.tgz```.
Default model name is ```pilot-wip.h5```.

### Start salient makemovie using google ai-platform

```bash
./submit_cloud_makemovie [-m <model.h5>] [-a <archive name>]
```

Default archive name is ```wip.tgz```.
Default model name is ```pilot-wip.h5```.

### Download resulting models

```bash
./download_models [-m <model basename>]
```

Default model name is ```pilot-wip```.

It will download all available models matching basename (provided or default one), meaning that <basemodel>.h5, <basemodel>.tflite and <basemodel>.onnx will be downloaded if avaiable in the GCS bucket.

## What you need to look at

This code is somekind of wrapper arround donkeycar to allow to use google training platform to train donkeycar model, using donkeycar sourcecode as a single source of truth.
In setup.py, you will found 2 kind of dependencies :

- dependency to a donkeycar repo to use for training, for a given branch/tag : **Verify that git url and branch match your need**
- additional dependencies, comming from [pc] target extra requirements, but not deployed by ai-platform
