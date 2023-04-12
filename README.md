# Purpose :
Train your model using google ai-platform service (not free, arround 0.2€ per training on the basic keras linear model)
For 13k images, Training duration is about 13mins (9min to start the process, then 4 mins to unpack dataset, tain model and convert to tflite)

Beyond using gloud to train model, idea here is to rely on donkeycar source code for the training so that training your model using donkey cli, donkey ui, or this method, is the same, has the same level of featuresm and works the same way.

# Requirements (from https://cloud.google.com/ai-platform/docs/getting-started-keras):
- have a GCP account 
- install gcloud CLI
- pip install --upgrade google-api-python-client
- pip install --upgrade google-cloud-storage
- create a project with billing activated
- (optionnal) create service account, key, and download it (json file) #keep care of this file, do not expose it !
- create a bucket (used for storage of dataset, job temporary files and model created),
- create two directories in your bucket : training and models (training is used to store datasets, models is where trained model are stored)
- make sure following env variable are defined :
    - (optionnal is service account is used) GOOGLE_APPLICATION_CREDENTIALS, or (if service account not used) follow https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=fr#how-to
    - STEERING_BUCKET_NAME, for example : irn-71028-dvc-lab-robocar-pace92
    - REGION, for example : europe-west1
    - JOB_DIR, for example : gs://$STEERING_BUCKET_NAME/job

# usage :

## create dataset archive
use the ```make_steering_archive.sh``` script, from your 'car' directory

you must call this script from your "car" directory. The script will automatically include config.py and myconfig.py to your dataset, so that training will be based on it.

usage : 
```
./make_steering_archive.sh <tub directory>
```

Default tub directory is ```data```.

You can specify another directory or subdirectory like :
```
./make_steering_archive.sh data/steering_data
```

## upload archive to your GCS bucket
use the ```upload_steering_archive.sh``` script

The script will upload archive to subdirectory training

usage : 
```
./make_steering_archive.sh <archive>
```

Archive is the file you got using ```make_steering_archive.sh``` script

## start local training (usefull at least to check that everything is fine) :
```
./local_train.sh <archive>
``` 

## start training using google ai-platform :
```
./submit_cloud_train <archive>
``` 

## start local salient makemovie (usefull at least to check that everything is fine) :
```
./local_makemovie.sh <archive> <model.h5>
``` 

## start training using google ai-platform :
```
./submit_cloud_makemovie <archive> <model.h5>
``` 


# What you need to look at :
This code is somekind of wrapper arround donkeycar to allow to use google training platform to train donkeycar model, using donkeycar sourcecode as a single source of truth. 
In setup.py, you will found 2 kind of dependencies :
- dependency to a donkeycar repo to use for training, for a given branch/tag
- additional dependencies, comming from [pc] target extra requirements, but not deployed by ai-platform  