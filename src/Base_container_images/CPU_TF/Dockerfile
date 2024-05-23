# Start from the official TensorFlow Docker image
FROM tensorflow/tensorflow:2.11.1

# Install opencv, requests and flask
RUN /usr/bin/python3 -m pip install opencv-python==4.8.0.76 requests==2.28.2 flask==2.3.2

# Redis necessary
RUN /usr/bin/python3 -m pip install redistimeseries==1.4.5 python-dotenv==1.0.0

# Workaround for a bug in cv2
# Update and install necessary system dependencies
RUN apt-get update -y && \
    apt-get install libglib2.0-0=2.64.6-1~ubuntu20.04.6 -y && \
    apt-get install libgl1=1.3.2-1~ubuntu0.20.04.2 -y
