#!/bin/bash

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Go back to root
cd ..

echo "✅ Setup complete! Run 'docker-compose up' to start the app."
