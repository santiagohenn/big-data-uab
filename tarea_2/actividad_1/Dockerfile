# Dockerfile: Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Update system packages and install any needed packages specified in requirements.txt
RUN apt-get update && apt-get dist-upgrade -y && apt-get install --only-upgrade -y python3 && pip install --upgrade pip && pip install --trusted-host pypi.python.org -r requirements.txt && apt-get clean && rm -rf /var/lib/apt/lists/*

# Make port 80 available to the world outside this container
# Define environment variable
# ENV NAME World
# Run app.py when the container launches
CMD ["python", "app.py"]