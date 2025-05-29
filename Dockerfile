ARG ARCH=
ARG CUDA=12.8.1
ARG UBUNTU_VERSION=22.04
FROM nvidia/cuda${ARCH:+-$ARCH}:${CUDA}-base-ubuntu${UBUNTU_VERSION} as base
# ARCH and CUDA are specified again because the FROM directive resets ARGs
# (but their default value is retained if set previously)
ARG ARCH
ARG CUDA

# Set environment variables
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV API_PORT=5001
ENV API_HOST=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY server.py .

# Expose the port the app runs on
EXPOSE ${API_PORT}

# Command to run the application
CMD ["python3", "server.py"]