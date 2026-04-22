FROM python:3.11-slim

# System deps: ffmpeg (H.264 transcode), rclone, curl
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    && curl https://rclone.org/install.sh | bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install -U yt-dlp

COPY scraper-fixed.py .

# rclone config will be mounted as a secret/configmap at runtime
# links.txt will be mounted as a configmap at runtime

CMD ["python", "scraper-fixed.py"]
