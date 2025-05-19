# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libmariadb-dev \
    default-mysql-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt


# Copy the entire project to the container
COPY . .

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Command to run Gunicorn as the WSGI server
# CMD ["gunicorn", "--bind", "0.0.0.0:8001", "medical_books.wsgi:application"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "bopo_backend.asgi:application"]

   