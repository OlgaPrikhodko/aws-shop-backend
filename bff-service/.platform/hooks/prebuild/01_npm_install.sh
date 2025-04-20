#!/bin/bash
cd /var/app/staging

# Install dependencies
npm install

# Install TypeScript globally
npm install -g typescript

# Build the application
npm run build

# Log the result
echo "Build completed"
ls -la dist/
