# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the environment variable for the bot token
ENV DISCORD_TOKEN=""

# Run the bot
CMD ["python3", "bot.py"]
