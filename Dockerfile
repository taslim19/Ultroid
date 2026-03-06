FROM ubuntu:22.04

# Set timezone
ENV TZ=Asia/Kolkata
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Python 3.11 and required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    ca-certificates \
    gnupg2 \
    gdb \
    git \
    gcc \
    ffmpeg \
    mediainfo \
    curl \
    neofetch \
&& mkdir -p /usr/share/keyrings \
&& curl -fsSL https://keyserver.ubuntu.com/pks/lookup?op=get\&search=0xF23C5A6CF475977595C89F51BA6932366A755776 | gpg --dearmor -o /usr/share/keyrings/deadsnakes.gpg \
&& echo "deb [signed-by=/usr/share/keyrings/deadsnakes.gpg] http://ppa.launchpad.net/deadsnakes/ppa/ubuntu jammy main" > /etc/apt/sources.list.d/deadsnakes-ppa.list \
&& apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
&& curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 \
&& update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
&& update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m user

# Set working directory
WORKDIR /app

# Copy project files
COPY . .


# List all files
RUN ls -la

# Avoid pip install as root errors
ENV PIP_ROOT_USER_ACTION=ignore
ENV PATH="/home/user/.local/bin:$PATH"

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir uvicorn fastapi
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Ensure required directories exist
RUN mkdir -p /app/sessions /app/resources/auth /app/tmp /app/pdf /app/addons && \
    chmod -R 777 /app/sessions /app/resources /app/tmp /app/pdf /app/addons && \
    chown -R user:user /app

# Fix relative imports (make packages)
RUN touch /app/__init__.py /app/addons/__init__.py /app/pyUltroid/__init__.py

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Switch to non-root user
USER user

# Run both the background server and the main bot startup script
CMD python3 server.py & bash startup