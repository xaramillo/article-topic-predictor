# Build an image for training and inference Topic tagging
# Uses the nginx, gunicorn, flask stack for serving inferences.

FROM ubuntu:20.04

# Maintainer (optional, but can be added for clarity)
# MAINTAINER xaramillo

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC


# 1. Install required system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    python3 \
    python3-dev \
    python3-distutils \
    python3-apt \
    nginx \
    libffi-dev \
    libssl-dev \
    gcc \
    pkg-config \
    libhdf5-dev \
    tzdata \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone non-interactively
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata

COPY requirements.txt .

# 2. Install Python packages
# Use wget to get pip, install required Python packages, and clean up afterward.
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    tensorflow==2.13.0 \
    transformers==4.35.2 \
    sentence-transformers==2.3.0 \
    pandas \
    numpy \
    flask \
    gevent \
    gunicorn && \
    rm -rf /root/.cache && \
    pip install -r requirements.txt

# 3. Set environment variables
# Ensure unbuffered output for Python logs and prevent .pyc files.
ENV PYTHONUNBUFFERED=TRUE \
    PYTHONDONTWRITEBYTECODE=TRUE \
    PATH="/opt/program:${PATH}" \
    LOG4J_FORMAT_MSG_NO_LOOKUPS=true
    #LD_PRELOAD='/PATH/TO/libgomp-d22c30c5.so.1.0.0'

# This line is necesary to load transformers library    
RUN export LD_PRELOAD='/usr/local/lib/python3.8/dist-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0'


# 4. Set working directory and copy inference code
# Define the folder for model files and code.
COPY topic_classifier /opt/program
WORKDIR /opt/program


# 5. Run the serve script
RUN chmod +x ./serve
CMD ["./serve"]
# ENTRYPOINT ["/bin/python3"]

# After this build, run the docker with:
    # docker run -p 8090:8090 -it --rm openalex-topic-classifier

