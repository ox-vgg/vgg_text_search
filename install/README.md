Deployment scripts
==================

These scripts are meant for local deployment on your computer of the applications listed here. This means that they will download and install third-party software and data in your computer, as well as compile and configure source code. The scripts are experimental and are intended for **Software Developers**. Regular users are strongly advised to use the docker version of the applications listed here to install them on their computers.

In all cases, you will need Python 3 installed on your system. For GPU support you will need the NVIDIA drivers and the CUDA Toolkit in your system. Please be aware that GPU support depends on your particular CUDA setup (version, location of the CUDA library in your system, etc.).

All scripts contain requirements and some instructions at the beginning of the file. Please read them before attempting the deployment.

Applications
------------

#### *VGG Text Search - Index only*

Use the `index_install_ubuntu.sh` script to deploy the application. This will deploy only the necessary sofware to build and execute the text-index, as well as to perform text searches on the index later on.

#### *VGG Text Search - Full system*

Use the `full_system_install_ubuntu.sh` script to deploy the application. This will deploy the same software than the *index only* version, but also a text-recognition package and scripts that can be used to process a set of images or a video and automatically build the text-index.
