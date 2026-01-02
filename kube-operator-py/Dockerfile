FROM python:3.11-slim

LABEL maintainer="EdgeLake Team"
LABEL description="Kubernetes Operator for EdgeLake operator nodes"

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 operator
USER operator

# Run operator
CMD ["kopf", "run", "--standalone", "--all-namespaces", "src/edgelake_operator/operator.py"]
