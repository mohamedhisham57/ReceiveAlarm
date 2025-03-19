# Use an official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app


# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc g++ make \
    && rm -rf /var/lib/apt/lists/*
    
# Copy necessary files into the container
COPY requirements.txt /app/requirements.txt
RUN ls -l /app/requirements.txt  # Debugging step
RUN cat /app/requirements.txt    # Debugging step
# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY run.sh /app/run.sh
COPY router-sms-sender/main.py /app/main.py

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make the run.sh script executable
RUN chmod +x /app/run.sh

# Set entrypoint
CMD ["/app/run.sh"]
