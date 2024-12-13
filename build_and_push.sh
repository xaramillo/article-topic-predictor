#!/usr/bin/env bash

# This script shows how to build the Docker image and push it to ECR to be ready for use
# by SageMaker.

# The argument to this script is the image name. This will be used as the image on the local
# machine and combined with the account and region to form the repository name for ECR.
image=${1}

if [ "$image" == "" ]
then
    echo "Usage: $0 <image-name>"
    exit 1
fi

chmod +x topic_classifier/serve

# Authenticate with GCP and configure Docker to use GCP registries
gcloud auth configure-docker

# Define GCP project and region
#project_id="670746971623" # Hardcoded
project_id=$(gcloud config get-value project)
if [ "$project_id" == "" ]; then
    echo "GCP project is not set. Use 'gcloud config set project <PROJECT_ID>' to set it."
    exit 1
fi

region=${region:-us-central1}

# Define the full image name for GCP's Container Registry (GCR)
fullname="gcr.io/${project_id}/${image}:latest"

# Build the docker image locally with the image name and then push it to ECR
# with the full name.

docker build  -t ${image} .
docker tag ${image} ${fullname}

docker push ${fullname}
