# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY app/ /app/app/

# Make port 8000 available to the world outside this container (default, overridden by env var)
EXPOSE 8000

# Run the application using uvicorn
# We use 0.0.0.0 to bind to all network interfaces.
# The port is read from the APP_PORT environment variable, defaulting to 8000 if not set.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${APP_PORT:-8000}"]