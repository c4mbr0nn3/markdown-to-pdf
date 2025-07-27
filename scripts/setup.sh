#!/bin/bash

# Markdown to PDF API Setup Script

set -e

echo "Setting up Markdown to PDF API..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p output

# Set up pre-commit hooks if available
if command -v pre-commit &> /dev/null; then
    echo "Setting up pre-commit hooks..."
    poetry run pre-commit install
fi

# Run code quality checks
echo "Running code quality checks..."
poetry run black --check app/ || echo "Run 'poetry run black app/' to format code"
poetry run isort --check-only app/ || echo "Run 'poetry run isort app/' to sort imports"
poetry run flake8 app/ || echo "Fix flake8 issues before running"

# Validate template files
echo "Validating template files..."
python -c "
from app.services.pdf_generator import PDFGenerator
pdf_gen = PDFGenerator()
if pdf_gen.validate_requirements():
    print('✓ Template files validation passed')
else:
    print('✗ Template files validation failed')
    exit(1)
"

echo "Setup completed successfully!"
echo ""
echo "To start the development server:"
echo "  poetry run uvicorn app.main:app --reload"
echo ""
echo "To start with Docker:"
echo "  docker build -t markdown-pdf-api . && docker run -p 8000:8000 markdown-pdf-api"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"