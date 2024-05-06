# Use an official Python runtime as a parent image with mirror URL
FROM python:3.9

# Set environment variables to use GCE mirror links
ENV DEBIAN_FRONTEND=noninteractive \
    APT_MIRROR="http://mirror.gce.com/debian"

# Update package list using mirror link
RUN sed -i "s|http://deb.debian.org/debian|$APT_MIRROR|g" /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV DEBUG true

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "index:app"]
