# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Set PYTHONPATH to include /app so module imports work correctly
ENV PYTHONPATH=/app

# Run the bot when the container launches
CMD ["python", "-m", "src.main_bot"]
