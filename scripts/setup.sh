#!/bin/bash

# VulnPatch AI Setup Script

echo "Setting up VulnPatch AI..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file for backend
echo "Creating environment configuration..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "SUCCESS: Created backend/.env file. Please update with your API keys."
else
    echo "WARNING: backend/.env already exists. Skipping..."
fi

# Create uploads directory
mkdir -p backend/uploads/reports
echo "SUCCESS: Created uploads directory"

# Build and start services
echo "Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 20

echo "Services are starting up..."
echo "Database migrations and demo user creation are handled automatically by the backend service."

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your Gemini API key"
echo "2. Access the application at http://localhost:3000"
echo "3. Use demo credentials: demo@vulnpatch.ai / demo123"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f          # View logs"
echo "  docker-compose down             # Stop services"
echo "  docker-compose up -d            # Start services"