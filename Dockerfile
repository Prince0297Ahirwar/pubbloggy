# Use the official Python image from the Docker Hub
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app
COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt
# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages


# Set the environment variable
ENV FLASK_APP=run.py

# Open the required port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]


