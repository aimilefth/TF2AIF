# Start from Xilinx's Vitis AI Docker image
FROM xilinx/vitis-ai:1.4.1.978

# Install necessary dependencies
RUN /usr/bin/python3 -m pip install --upgrade pip==21.2.4
RUN /usr/bin/python3 -m pip install tensorflow==2.6.2
RUN /usr/bin/python3 -m pip install opencv-python==4.6.0.66 requests==2.27.1 flask==2.0.2

# Redis necessary
RUN /usr/bin/python3 -m pip install redistimeseries==1.4.5 python-dotenv==0.20.0

# Workspace setup
ARG SETUP_DIR_ARG=/setup_dir
ARG SETUP_FILE_ARG=setup.sh
ENV SETUP_DIR=${SETUP_DIR_ARG}
ENV SETUP_FILE=${SETUP_FILE_ARG}

# Create working directory and copy setup file
RUN mkdir -p ${SETUP_DIR_ARG}
COPY ${SETUP_FILE} ${SETUP_DIR_ARG}

# Setting the working directory
WORKDIR ${SETUP_DIR_ARG}

# Modify permissions and ownership of setup file and working directory
RUN chmod u+x ${SETUP_FILE_ARG}
RUN chown -R vitis-ai-user:vitis-ai-group ${SETUP_DIR_ARG}