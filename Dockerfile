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

COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
COPY . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Expose the port the app runs on
EXPOSE ${API_PORT}

# Command to run the application
CMD ["uv", "run", "server.py"]