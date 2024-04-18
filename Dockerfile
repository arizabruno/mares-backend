# Use an official Python runtime as a parent image
FROM python:3.10.6-slim

WORKDIR /prod

COPY . /prod

# Install PostgreSQL development libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && \
    # Clean up the apt cache by removing /var/lib/apt/lists saves space
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE $PORT

# Run the FastAPI app using uvicorn when the container launches
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080
