# Start from Nvidia's L4T TensorFlow Docker image
FROM nvcr.io/nvidia/l4t-tensorflow:r32.7.1-tf2.7-py3

RUN python3 -m pip install --upgrade pip==21.3.1

# Install opencv, requests and flask
RUN python3 -m pip install opencv-python==4.6.0.66 requests==2.27.1 flask==2.0.3

# Redis necessary
RUN python3 -m pip install redistimeseries==1.4.5 python-dotenv==0.20.0

#Mismatch of the Nvidia's L4T TensorFlow Docker image. Keras version was 2.8.0 and this caused bugs with some models
RUN python3 -m pip install keras==2.7.0

# Environment Variable to preload a library
ENV LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1

# Use this on host if docker buildx build errors like this : Error while loading /usr/sbin/dpkg-split: No such file or directory 
# docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
