#!/bin/bash
# Frontend development server startup script
# This script starts the Vue.js frontend dev server with the correct environment variables

cd "$(dirname "$0")"
NODE_OPTIONS=--openssl-legacy-provider TARGET=http://localhost:8000 npm run dev
