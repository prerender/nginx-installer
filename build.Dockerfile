# Use an official Python runtime as a parent image
FROM python:3.13

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PyInstaller
RUN pip install pyinstaller

# Create the standalone executable
RUN pyinstaller --onefile src/main.py

# Create the /bin directory in the project root if it doesn't exist
RUN mkdir -p /usr/src/app/bin

# Move the executable to the /bin directory
RUN mv dist/main /usr/src/app/bin/

# Define the entrypoint
ENTRYPOINT ["/usr/src/app/bin/main"]