name: DevSecOps Pipeline (Matrix Optimized)

on:
  push:
    branches: [ "main" ]
    paths:
      - 'service_a/**'
      - 'service_b/**'
      - '.github/workflows/ci-security.yaml'

permissions:
  contents: write
  packages: write
  security-events: write

jobs:
  # ------------------------------------------------------------------
  # JOB 1 : Sécurité Globale (S'exécute 1 seule fois pour tout le repo)
  # ------------------------------------------------------------------
  global-security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Historique complet pour Gitleaks

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        # Note: J'ai retiré 'verbose: true' car l'action v2 ne le supporte pas en input direct
        # et cela créait ton Warning.

  # ------------------------------------------------------------------
  # JOB 2 : Build & Deploy par Service (S'exécute en parallèle pour A et B)
  # ------------------------------------------------------------------
  build-and-deploy:
    # Ce job attend que le scan global soit fini et OK
    needs: global-security-scan
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        service: [service_a, service_b]

    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      # --- SAST (Bandit) ---
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install Security Tools
        run: pip install bandit

      - name: Run Bandit (SAST)
        # On scanne uniquement le dossier du service
        run: bandit -r ./${{ matrix.service }}

      # --- SCA (Trivy FS) ---
      - name: Run Trivy vulnerability scanner (SCA)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: './${{ matrix.service }}'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'

      # --- Build Local ---
      - name: Build Local Image for Scanning
        run: |
          cd ${{ matrix.service }}
          docker build -t ${{ matrix.service }}:latest .

      # --- Container Security (Trivy Image) ---
      - name: Run Trivy container scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ matrix.service }}:latest'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL'

      # --- Push GHCR ---
      - name: Log in to the Container registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: ./${{ matrix.service }}
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:latest

      # --- GitOps Update ---
      - name: Update Kubernetes Manifest
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"

          SERVICE_NAME="${{ matrix.service }}"
          IMAGE_NAME="ghcr.io/${{ github.repository }}/${SERVICE_NAME}:${{ github.sha }}"
          FILE_PATH="${SERVICE_NAME}/k8s/${SERVICE_NAME}.yaml"

          echo "Mise à jour de $FILE_PATH"

          sed -i "s|image: ghcr.io/.*|image: $IMAGE_NAME|g" $FILE_PATH
          
          # Gestion du pull/rebase pour éviter les conflits entre les 2 jobs
          git pull origin main --rebase || true

          git add $FILE_PATH
          git commit -m "Update ${SERVICE_NAME} image to ${{ github.sha }}" || echo "No changes"
          git push
