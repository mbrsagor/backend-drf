# Deployment Pipeline

![Pipeline](./pipeline.png)

## Overview
The pipeline is divided into three custom workflows:
- **Build and Push:** Builds a Docker image and pushes it to AWS Elastic Container Registry (ECR).
- **Deploy to EC2:** Deploys the Docker image to a production EC2 instance using Docker Compose.
- **Cleanup Instance:** Cleans up unused Docker images and dangling resources from the EC2 instance.

## Pipeline Configurations

### 1. Build and Push
This task builds a Docker image with the specified tag and pushes it to AWS ECR.

#### Input:
 - **ImageTag:** The tag for the Docker image (e.g., `v1`, `v2` or a specific version).

### 2. Deploy to EC2
This task deploys the application to an EC2 instance using Docker Compose.

#### Input:
 - **ImageTag:** The tag for the Docker image to deploy.

### 3. Cleanup Instance
This task cleans up dangling Docker images and unused containers to free up space on the EC2 instance.

`Note:` Please cleanup the instance often.

#### Input:
 - **AreYouSure:** A confirmation variable to prevent accidental execution (default: `No`).

## Usage Instructions
1. Go the bitbucket repository.
2. Select `Pipeline` option.
3. Click on `Run Pipeline` button.
4. Select a `preferred branch` and pipeline action to perform.
5. Click on `Run` button to trigger.


## [Go to README](./README.md)%  

