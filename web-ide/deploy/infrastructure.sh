#!/bin/bash
set -e

# ==============================================================================
# Azure Container Apps Infrastructure for Ajanta Web-IDE
# Uses ACR Build for cloud-based image building (works from any platform)
# ==============================================================================

# Configuration - Customize these values
RESOURCE_GROUP="ajanta-web-ide-rg"
LOCATION="eastus"
ACR_NAME="ajantawebideacr"
ENVIRONMENT_NAME="ajanta-web-ide-env"
BACKEND_APP_NAME="ajanta-backend"
FRONTEND_APP_NAME="ajanta-frontend"

echo "🚀 Setting up Azure infrastructure for Ajanta Web-IDE..."

# ==============================================================================
# Step 1: Create Resource Group
# ==============================================================================
echo "📦 Creating resource group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# ==============================================================================
# Step 2: Create Azure Container Registry
# ==============================================================================
echo "📦 Creating Azure Container Registry: $ACR_NAME..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

echo "✅ ACR created: $ACR_LOGIN_SERVER"

# Navigate to project root
cd "$(dirname "$0")/../.."

# ==============================================================================
# Step 3: Build and Push Docker Images using ACR Build
# ==============================================================================
echo "🔨 Building backend image in Azure cloud..."
az acr build \
  --registry $ACR_NAME \
  --image $BACKEND_APP_NAME:latest \
  --file web-ide/backend/Dockerfile \
  .

echo "🔨 Building frontend image in Azure cloud (with placeholder API URL)..."
az acr build \
  --registry $ACR_NAME \
  --image $FRONTEND_APP_NAME:latest \
  --build-arg NEXT_PUBLIC_API_URL=https://placeholder.azurecontainerapps.io \
  ./web-ide/frontend-next

# ==============================================================================
# Step 4: Create Container Apps Environment
# ==============================================================================
echo "🌍 Creating Container Apps Environment..."
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# ==============================================================================
# Step 5: Deploy Backend Container App
# ==============================================================================
echo "🚀 Deploying backend..."
az containerapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_LOGIN_SERVER/$BACKEND_APP_NAME:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi

# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv)

echo "✅ Backend deployed: https://$BACKEND_URL"

# ==============================================================================
# Step 6: Rebuild and Deploy Frontend with correct API URL
# ==============================================================================
echo "🔨 Rebuilding frontend with correct API URL..."
az acr build \
  --registry $ACR_NAME \
  --image $FRONTEND_APP_NAME:latest \
  --build-arg NEXT_PUBLIC_API_URL=https://$BACKEND_URL \
  ./web-ide/frontend-next

echo "🚀 Deploying frontend..."
az containerapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_LOGIN_SERVER/$FRONTEND_APP_NAME:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 3000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars NEXT_PUBLIC_API_URL=https://$BACKEND_URL

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv)

echo ""
echo "=============================================="
echo "🎉 Deployment Complete!"
echo "=============================================="
echo "Frontend URL: https://$FRONTEND_URL"
echo "Backend URL:  https://$BACKEND_URL"
echo "=============================================="
echo ""
echo "To test accessibility:"
echo "  curl -s -o /dev/null -w '%{http_code}' https://$FRONTEND_URL"
echo ""
