# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /prod

# Copy the entire project into the container
COPY . /prod

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
