#!/bin/bash

# Backend structure
mkdir -p backend/{app/{api,core,models,utils},queries,tests}
mkdir -p backend/app/api/{endpoints,deps}

# Frontend structure
mkdir -p frontend/{src/{components/{widgets,filters,layout},composables,config/dashboards,stores,utils,router,assets/{css,icons}},public}
mkdir -p frontend/src/components/{Dashboard,common}

# Root files
mkdir -p docker
mkdir -p docs

echo "Project structure created successfully!"
