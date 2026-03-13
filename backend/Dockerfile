FROM python:3.11-slim

WORKDIR /app

# System deps for mysqlclient + git
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install serve for static hosting
RUN npm install -g serve

COPY . .

EXPOSE 8000
