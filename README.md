# Purpose :
Train your model using google ai-platform service (not free, arround 0.2€ per training on the basic keras linear model)
For 13k images, Training duration is about 13mins (9min to start the process, then 4 mins to unpack dataset, tain model and convert to tflite)

Beyond using gloud to train model, idea here is to rely on donkeycar source code for the training so that training your model using donkey cli, donkey ui, or this method, is the same, has the same level of featuresm and works the same way.

# Requirements (from https://cloud.google.com/ai-platform/docs/getting-started-keras):
- have a GCP account 
- install gcloud CLI
- create a project with billing activated
- create service account, key, and download it (json file) #keep care of this file, do not expose it !
- create a bucket (used for storage of dataset, job temporary files and model created)
- make sure following env variable are defined :
    - GOOGLE_APPLICATION_CREDENTIALS
    - STEERING_BUCKET_NAME
    - REGION

# usage :

## create dataset archive
use the ```make_steering_archive.sh``` script, from your 'car' directory

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
./submit_cloud_job <archive>
``` 

# What you need to look at :
This code is somekind of wrapper arround donkeycar to allow to use google training platform to train donkeycar model, using donkeycar sourcecode as a single source of truth. 
In setup.py, you will found 2 kind of dependencies :
- dependency to a donkeycar repo, for a given branch/tag
- additional dependencies, comming from [pc] target extra requirements, but not deployed by ai-platform  