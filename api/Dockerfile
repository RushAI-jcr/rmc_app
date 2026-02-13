FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline and api code
COPY pipeline/ ./pipeline/
COPY api/ ./api/
COPY data/ ./data/

# Run uvicorn
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
