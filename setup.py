from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
        'opencv-python',
        'matplotlib',
        'kivy',
        'protobuf==3.20.3',
        'pandas',
        'pyyaml',
        'plotly',
        'imgaug',
#        'donkeycar @ git+https://github.com/btrinite/donkeycar-rrl.git@grumpy#egg=donkeycar',
        'donkeycar @ git+https://github.com/roboracingleague/donkeycar.git@rknn#egg=donkeycar',
    ]

setup(
    name='steering-trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='My training application package.'
)
