# ============================================================
# AWESOME-GRIZZLY-V1 - Multi-stage Dockerfile (Alpine)
# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:3.11-alpine AS builder

LABEL maintainer="Ian Carter Kulani"
LABEL description="AWESOME-GRIZZLY-V1 Ultimate Cyber Platform"

# Build dependencies
RUN apk add --no-cache --virtual .build-deps \
        gcc \
        g++ \
        musl-dev \
        linux-headers \
        libffi-dev \
        openssl-dev \
        libpcap-dev \
        jpeg-dev \
        zlib-dev \
        freetype-dev \
        tiff-dev \
        lcms2-dev \
        libwebp-dev \
        harfbuzz-dev \
        fribidi-dev \
        libimagequant-dev \
        libxcb-dev \
        libpng-dev \
        make \
        cmake \
        cargo \
        rust

WORKDIR /build

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Runtime
# ============================================================
FROM python:3.11-alpine AS runtime

LABEL maintainer="Ian Carter Kulani"
LABEL version="1.0.0"
LABEL description="AWESOME-GRIZZLY-V1 - Ultimate Multi-Platform Cybersecurity Platform"

# Runtime system tools
RUN apk add --no-cache \
        nmap \
        nmap-scripts \
        curl \
        wget \
        netcat-openbsd \
        bind-tools \
        traceroute \
        mtr \
        whois \
        openssh-client \
        openssl \
        bash \
        tini \
        ca-certificates \
        tzdata \
        libpcap \
        libjpeg-turbo \
        zlib \
        freetype \
        tiff \
        lcms2 \
        libwebp \
        harfbuzz \
        fribidi \
        libimagequant \
        libxcb \
        libpng \
        sqlite \
        chromium \
        chromium-chromedriver \
        xvfb \
        dbus \
        ttf-freefont

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user (will be overridden when needed)
RUN addgroup -g 1000 grizzly && \
    adduser -u 1000 -G grizzly -s /bin/bash -D grizzly

WORKDIR /app

# Copy application files
COPY --chown=grizzly:grizzly awesome_grizzly.py .
COPY --chown=grizzly:grizzly requirement-check.py .
COPY --chown=grizzly:grizzly test-commands.py .
COPY --chown=grizzly:grizzly requirements.txt .
COPY --chown=grizzly:grizzly README.md .

# Create application directories
RUN mkdir -p /app/.awesome_grizzly_v1 \
             /app/awesome_grizzly_reports \
             /app/data && \
    chown -R grizzly:grizzly /app

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:/usr/local/bin:$PATH" \
    GRIZZLY_HOME=/app \
    GRIZZLY_DATA=/app/data \
    CHROME_BIN=/usr/bin/chromium-browser \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99

# Volume for persistent data
VOLUME ["/app/.awesome_grizzly_v1", "/app/awesome_grizzly_reports", "/app/data"]

# Expose ports: web dashboard + phishing + C2
EXPOSE 5000/tcp 8080/tcp 4444/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/stats', timeout=5)" || exit 1

# Entry point
USER root
COPY --chown=root:root docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "awesome_grizzly.py"]
