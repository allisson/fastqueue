##### Builder Stage #####
FROM python:3.10-slim as builder

# Set default path
ENV PATH="/app/.venv/bin:${PATH}"

# Set default workdir
WORKDIR /app

# Create virtualenv and install Python packages
RUN pip install --no-cache-dir pip -U && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.in-project true
COPY ./poetry.lock poetry.lock
COPY ./pyproject.toml pyproject.toml
RUN poetry install --only main

# Copy app files and add directory to workdir
COPY fastqueue ./fastqueue

##### Final Stage #####
FROM python:3.10-slim

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Set default path
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH /app

# Copy content from builder stage
COPY --from=builder /app /app

# Install packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y tini && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add fastqueue user and create directories
RUN useradd -m fastqueue && mkdir -p /app

# Set permissions
RUN chown -R fastqueue:fastqueue /app

# Set workdir and XAPO User
WORKDIR /app
USER fastqueue

# Set entrypoint and cmd
ENTRYPOINT ["/usr/bin/tini", "--", "python", "/app/fastqueue/main.py"]
CMD ["server"]
