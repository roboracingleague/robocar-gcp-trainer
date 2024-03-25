# Specifies base image and tag
# https://cloud.google.com/vertex-ai/docs/training/pre-built-containers?hl=fr
# python 3.7 fwk 2.9
# FROM europe-docker.pkg.dev/vertex-ai/training/tf-cpu.2-9:latest
FROM europe-docker.pkg.dev/vertex-ai/training/tf-gpu.2-9:latest
# FROM europe-docker.pkg.dev/vertex-ai/training/tf-gpu.2-11:latest

WORKDIR /root

# Create a distinct layer with deps for faster dev cycle
COPY ./setup.py /root/setup.py
RUN python setup.py egg_info && \
    pip install -r *.egg-info/requires.txt && \
    rm -rf *.egg-info/

COPY . /root/

RUN pip install --no-deps .

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "-m", "task.train"]