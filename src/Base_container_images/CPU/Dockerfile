# Start from Intel's optimized TensorFlow Docker image
FROM intel/intel-optimized-tensorflow:tf2.11.0-ubuntu-22.04

# Update and install necessary system dependencies
RUN apt-get update && \
    apt-get install ffmpeg=7:4.4.2-0ubuntu0.22.04.1 libsm6=2:1.2.3-1build2 libxext6=2:1.3.4-1build1  -y

# Install opencv, requests and flask
RUN /usr/bin/python3 -m pip install opencv-python==4.8.0.76 requests==2.28.2 flask==2.3.3

# Redis necessary
RUN /usr/bin/python3 -m pip install redistimeseries==1.4.5 python-dotenv==1.0.0