# Specifies base image and tag
# python 3.7 fwk 2.9
FROM europe-docker.pkg.dev/vertex-ai/training/tf-cpu.2-9:latest
WORKDIR /root

# Installs additional packages
#RUN pip install 'donkeycar @ git+https://github.com/roboracingleague/donkeycar.git@main#egg=donkeycar'
# RUN pip install 'steering-trainer @ git+https://github.com/roboracingleague/robocar-gcp-trainer.git@master#egg=steering-trainer'

COPY ./setup.py /root/setup.py

RUN python setup.py egg_info && \
    pip install -r *.egg-info/requires.txt && \
    rm -rf *.egg-info/

COPY . /root/

RUN pip install --no-deps .

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "-m", "task.train"]