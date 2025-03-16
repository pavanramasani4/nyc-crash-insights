# Use the official Python image as a base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Ensure the 'WebPage' directory exists
RUN mkdir -p /app/WebPage

# Create an empty database file with appropriate permissions
RUN touch /app/WebPage/mydatabase.db
RUN chmod 644 /app/WebPage/mydatabase.db

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=Week1.py
ENV PYTHONPATH=/app

# Set the working directory to /app/WebPage
WORKDIR /app/WebPage

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]