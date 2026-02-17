#!/bin/bash

# Quick Start Script for Configurable Dashboard System
# This script helps you get started quickly

set -e

echo "🚀 Configurable Dashboard System - Quick Start"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create .env files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
fi

echo ""
echo "🐳 Starting Docker containers..."
echo "   This may take a few minutes on first run..."
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ All services are running!"
    echo ""
    echo "📊 Access your dashboard system:"
    echo "   Frontend:  http://localhost:5173"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📚 Quick Tips:"
    echo "   • View logs: docker-compose logs -f"
    echo "   • Stop system: docker-compose down"
    echo "   • Restart: docker-compose restart"
    echo ""
    echo "📖 Read the Getting Started guide:"
    echo "   docs/getting-started.md"
    echo ""
    echo "🎉 Happy dashboard building!"
else
    echo ""
    echo "⚠️  Some services may not be running correctly."
    echo "   Check logs: docker-compose logs"
    exit 1
fi
