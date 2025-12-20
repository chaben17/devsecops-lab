name: Frontend Pipeline

on:
  push:
    branches: [ "main" ]
    paths:
      - 'frontend/**'                # Se déclenche UNIQUEMENT si on touche au frontend
      - '.github/workflows/ci-frontend.yaml'

jobs:
  build-frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write                # Nécessaire pour pousser sur GHCR

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    # On configure Docker
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    # Connexion au registre GitHub (GHCR)
    - name: Log in to the Container registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    # Build et Push DIRECT (Pas de Python, pas de Scan)
    - name: Build and Push Docker image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ghcr.io/${{ github.repository_owner }}/devsecops-lab/frontend:latest
