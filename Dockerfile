# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY app.py .
COPY clean.py .

# Create a directory for logs
RUN mkdir -p /app/logs

# Run app.py when the container launches
CMD ["python", "-u", "app.py"]
