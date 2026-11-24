#!/usr/bin/env bash
# Build script for Vercel deployment
echo "Building project assets for Vercel..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "Build completed successfully."
