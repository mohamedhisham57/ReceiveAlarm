# Base image for Home Assistant add-ons with Python
FROM ghcr.io/home-assistant/amd64-base-python:3.11

# Set environment variables
ENV LANG C.UTF-8

# Create working directory
WORKDIR /app

# Copy local files into container
COPY run.py run.py
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint
CMD ["python3", "/app/main.py"]
