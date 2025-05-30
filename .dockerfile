# Example for a Python + FastAPI app
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set CARGO_HOME to a writable directory to avoid read-only FS error
ENV CARGO_HOME=/tmp/cargo

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app with uvicorn on port 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
