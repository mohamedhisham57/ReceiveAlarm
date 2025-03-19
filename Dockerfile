# Use an official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy necessary files into the container
COPY requirements.txt .
COPY run.sh /app/run.sh
COPY main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the run.sh script executable
RUN chmod +x /app/run.sh

# Set entrypoint
CMD ["/app/run.sh"]
