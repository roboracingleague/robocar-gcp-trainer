#!/usr/bin/env python3
"""
Scripts to manage car data

    # Collect data
    # Clean data
    # Train model
    # Download model
    # Push model

Usage:
    Before using this script, env MUST be set
        REMOTE_USERNAME : username on car
        REMOTE_PASSWORD : user password on car
        STEERING_BUCKET_NAME : gcp bucket used
        REGION : gcp region
        JOB_DIR : gcp job bucket
        CAR_IP_NAME : facultative

        and
        gcloud auth login ...
        gcloud auth application-default login
        
    manage_cardata.py (clean) [--car=<ip|name>]
        To clean folder before recording
    
    manage_cardata.py (collect) [--car=<ip|name>]
        To collect compressed data from car

    manage_cardata.py (push) [--car=<ip|name>]  
        To push model to car
    
    manage_cardata.py (steps)  
        To see parametrized steps
    
    manage_cardata.py (drive) [--car=<ip|name>]  
        To launch model on car
        
    
Options:
    -h --help               Show this screen.
"""
import os
import paramiko
import time
from docopt import docopt
from pathlib import Path

# Define the remote server information  
car_server_port = 22
car_server_username = os.environ.get('REMOTE_USERNAME')
car_server_password = os.environ.get('REMOTE_PASSWORD')

def move_data_folder_to_record(car_name):

   # Create a new SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh_client.connect(car_name, car_server_port, car_server_username, car_server_password)

    # Make a backup and move data folder
    timestamp = time.strftime('%Y%m%d%H%M%S')
    stdin, stdout, stderr = ssh_client.exec_command(f'mv mycar/data mycar/data{timestamp}')

    # Close the SSH connections
    ssh_client.close()

def collect(car_name):

    # Define the local and remote file paths and names
    car_data_folder_name = 'mycar/data'
    car_data_folder_path = f'/home/{car_server_username}/{car_data_folder_name}'
    timestamp = time.strftime('%Y%m%d%H%M%S')
    data_tar_file_name = 'data{timestamp}.tgz'
    local_compressed_file_path = f'data{timestamp}/{data_tar_file_name}'

    # Create a new SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh_client.connect(car_name, car_server_port, car_server_username, car_server_password)

    # Create the remote folder for the data if it doesn't exist
    # stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {car_data_folder_path}')

    # Compress the data folder on the remote server
    stdin, stdout, stderr = ssh_client.exec_command(f'cd /home/{car_server_username}/mycar && tar czf {data_tar_file_name} data')

    # Transfer the compressed file from the remote server to the local computer
    sftp_client = ssh_client.open_sftp()
    sftp_client.get(f'/home/{car_server_username}/mycar/{data_tar_file_name}', local_compressed_file_path)

    # Close the SFTP connections
    sftp_client.close()

    # Close the SSH connections
    ssh_client.close()

    # Uncompress the compressed file on the local computer
    os.system(f'tar xzf {data_tar_file_name} -C /home/{car_server_username}/mycar/data{timestamp}')

    # copy config.py to complete directory data
    os.system(f'cp config.py data{timestamp}/config.py -C /home/{car_server_username}/mycar')

    # copy myconfig.py to complete directory data
    os.system(f'cp myconfig.py data{timestamp}/myconfig.py -C /home/{car_server_username}/mycar')

    steps(f'data{timestamp}')

def steps(parent_dir_name):

    print(f'next steps to run from {parent_dir_name} directory')
    print(f'~/github/robocar-gcp-trainer/make_tub_archive.sh data {parent_dir_name}a')
    print(f'~/github/robocar-gcp-trainer/upload_dataset_archive.sh {parent_dir_name}a.tgz')
    print(f'~/github/robocar-gcp-trainer/submit_cloud_job.sh {parent_dir_name}a.tgz')
    print(f'~/github/robocar-gcp-trainer/download_model.sh pilot-{parent_dir_name}a.onnx')
    print(f'manage_cardata.py (push) [--car=<ip|name>]')
    print(f'to drive the car:')
    print(f'python manage.py drive --model ~/mycar/models/pilot-{parent_dir_name}a.onnx --type onnx_linear')

def push(car_name):
    # Create a new SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh_client.connect(car_name, car_server_port, car_server_username, car_server_password)

    parent_dir = Path().resolve().parent
    parent_dir_name = str(parent_dir).split('/')[-1]
    model_name = f'pilot-{parent_dir_name}a.onnx'

    # Transfer the compressed file from the remote server to the local computer
    sftp_client = ssh_client.open_sftp()
    sftp_client.put(f'{model_name}', f'/home/{car_server_username}/mycar/models/{model_name}')
    
    # Close the SFTP connections
    sftp_client.close()

    # Close the SSH connections
    ssh_client.close()

def drive(car_name):
    # Create a new SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh_client.connect(car_name, car_server_port, car_server_username, car_server_password)

    parent_dir = Path().resolve().parent
    parent_dir_name = str(parent_dir).split('/')[-1]
    model_name = f'pilot-{parent_dir_name}a.onnx'

    # Compress the data folder on the remote server
    stdin, stdout, stderr = ssh_client.exec_command(f'python manage.py drive --model ~/mycar/models/{model_name} --type onnx_linear')

    # Close the SSH connections
    ssh_client.close()

if __name__ == '__main__':
    args = docopt(__doc__)

    if args['clean']:
        if args['--car']:
            move_data_folder_to_record(car_name=args['--car'])
        else:
            move_data_folder_to_record(car_name=os.environ.get('CAR_IP_NAME'))
    
    elif args['collect']:
        if args['--car']:
            collect(car_name=args['--car'])
        else:
            collect(car_name=os.environ.get('CAR_IP_NAME'))

    elif args['train']:
        print(f'use finer shell scripts')
    
    elif args['push']:
        if args['--car']:
            push(car_name=args['--car'])
        else:
            push(car_name=os.environ.get('CAR_IP_NAME'))

    elif args['steps']:
        parent_dir = Path().resolve().parent
        parent_dir_name = str(parent_dir).split('/')[-1]    
        steps(parent_dir_name=parent_dir_name)
    
    elif args['drive']:
        if args['--car']:
            drive(car_name=args['--car'])
        else:
            drive(car_name=os.environ.get('CAR_IP_NAME'))