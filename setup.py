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
        'tf2onnx',
        'moviepy',
        'keras-vis @ git+https://github.com/autorope/keras-vis.git@master#egg=keras-viz',
        'donkeycar @ git+https://github.com/roboracingleague/donkeycar.git@main#egg=donkeycar',
    ]

setup(
    name='steering-trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='My training application package.'
)
