# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install tzdata for timezone support
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Create a directory for logs (matches the script's expectation or mapped volume)
RUN mkdir -p logs

# Environment variables
# Ensure output is sent directly to terminal (stdout/stderr) immediately
ENV PYTHONUNBUFFERED=1

# Set the entrypoint to the scheduler
CMD ["python", "scheduler.py"]
