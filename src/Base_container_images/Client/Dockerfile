# Start from the official Python Docker image
FROM python:3.9.16

# Update and install necessary system dependencies
RUN apt-get update && \
    apt-get install ffmpeg=7:4.3.6-0+deb11u1 libsm6=2:1.2.3-1 libxext6=2:1.3.3-1.1  -y

# Install necessary Python dependencies
RUN pip install opencv-python==4.7.0.68 requests==2.28.2 flask==2.2.2 matplotlib==3.6.3