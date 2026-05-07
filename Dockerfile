# FINESE_ONE/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for reportlab or pptx)
# RUN apt-get update && apt-get install -y libxml2-dev libxslt1-dev

# Copy requirements
COPY requirements-spaces.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]