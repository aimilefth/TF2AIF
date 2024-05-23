# Start from the official TensorFlow Docker image with GPU support
FROM tensorflow/tensorflow:2.11.1-gpu

# Install necessary Python dependencies
RUN /usr/bin/python3 -m pip install onnx==1.13.1 onnxruntime-gpu==1.14.0 opencv-python==4.8.0.76 requests==2.22.0 flask==2.3.2

# Redis necessary
RUN /usr/bin/python3 -m pip install redistimeseries==1.4.5 python-dotenv==1.0.0

# Workaround for a bug in cv2
# Update and install necessary system dependencies
RUN apt-get update -y && \
    apt-get install libgl1=1.3.2-1~ubuntu0.20.04.2 -y

# Workaround for this bug https://stackoverflow.com/questions/74956134/could-not-load-dynamic-library-libnvinfer-so-7
RUN cd /usr/lib/x86_64-linux-gnu/ && \
    ln -s libnvinfer_plugin.so.8 libnvinfer_plugin.so.7 && \
    ln -s libnvinfer.so.8 libnvinfer.so.7