# Start from ARM's TensorFlow Docker image
FROM armswdev/tensorflow-arm-neoverse:r23.04-tf-2.11.0-onednn-acl_threadpool

# Update and install necessary system dependencies
USER root
RUN apt-get update && \
    apt-get install ffmpeg=7:4.4.2-0ubuntu0.22.04.1 libsm6=2:1.2.3-1build2 libxext6=2:1.3.4-1build1  -y

# Install opencv, requests and flask
RUN python3 -m pip install opencv-python==4.6.0.66 requests==2.28.2 flask==2.3.3

# Redis necessary
RUN python3 -m pip install redistimeseries==1.4.5 python-dotenv==1.0.0

# Set environment variable to preload a library
ENV LD_PRELOAD=/lib/aarch64-linux-gnu/libGLdispatch.so.0