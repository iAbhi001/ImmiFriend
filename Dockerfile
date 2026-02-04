# 1. Use a lightweight Python image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies for ChromaDB and PDF parsing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the locked file structure
COPY . .

# 6. Expose the port Streamlit uses
EXPOSE 8501

# 7. Run the app
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]