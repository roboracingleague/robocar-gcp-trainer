from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
        'opencv-python',
        'matplotlib',
        'kivy',
        'protobuf==3.19.6',
        'pandas',
        'pyyaml',
        'plotly',
        'imgaug',
        'onnx==1.12.0',
        'tf2onnx',
#        'donkeycar @ git+https://github.com/btrinite/donkeycar-rrl.git@grumpy#egg=donkeycar',
        'donkeycar @ git+https://github.com/roboracingleague/donkeycar.git@obo-perf#egg=donkeycar',
    ]

setup(
    name='steering-trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='My training application package.'
)
