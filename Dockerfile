FROM python

# Set working directory in the container
WORKDIR /app
COPY . .
# Copy requirements file and install dependencies

RUN pip install -r reqiurenment.txt

# Copy the application code into the container


# Expose port 5000 for Flask application
EXPOSE 5001

# Command to run the Flask application
CMD ["python", "app.py"]
