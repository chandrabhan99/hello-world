# Use Python 3.11 image as base
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

# Create and set permissions for the Python environment directory
RUN mkdir -p /workspace/pythonenv3.11
RUN chmod 755 /workspace/pythonenv3.11

# Create symbolic link to directory (if needed)
RUN ln -s /workspace/pythonenv3.11 /app/pythonenv

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]