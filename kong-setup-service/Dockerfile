# Use the specified base image
FROM python:3.13.0-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run the setup script
CMD ["python", "run.py"]
