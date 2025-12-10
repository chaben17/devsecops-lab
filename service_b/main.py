from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import json
import os
from jose import JWTError, jwt

app = FastAPI()

# --- BLOC CORS À AJOUTER ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod, on mettrait l'URL précise du frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------

# --- CONFIGURATION SÉCURITÉ ---
# ⚠️ COLLE TA CLÉ PUBLIQUE ICI (La même que pour Service A)
PUBLIC_KEY_STR = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzM9ONo/+B47DNuL9uj7M7JBbLFDnC/PsUCrCeJQB+yFTpk1wEAQT4umvp0solPLXNaqk4vRjzOt1dbfsPyIzFoOEDFv58x9iSod6pdhjQEXwlWJG+W6io3Af9A2rcr8lXhSmgFpMC0oZZj3ZXCGCxJZm8kZEA85dgahX1Wp2RNAhh7SOKe5ZjN7ejSSramZlaeXTdtT2LVaCkzE5y58l9Pp9uCOn/85IE4R/1lfB2h/7KSYr80H1Uup4K7MyqzEbKDlpPdi+QTHefy1/yz/mdLuu6RwwO0fzGCp8mPs7SMGSY+tFIkcixDbLLil5TB420KJXyXlzzyMVHzOjcNpniQIDAQAB" 

PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"
ALGORITHM = "RS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM], audience="account")
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalide ou expiré: {str(e)}")
# -----------------------------

# Configuration du chemin vers les données
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = "/data/products.txt"

# Ajout de la protection "Depends(verify_token)"
@app.get("/products/{product_id}")
def get_product(product_id: str, token: dict = Depends(verify_token)):
# --- VÉRIFICATION RBAC (Nouveau bloc) ---
    roles = token.get("realm_access", {}).get("roles", [])
    
    # On vérifie si le rôle "reader" est présent
    if "reader" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : Vous n'avez pas le rôle 'reader'."
        )
    # ----------------------------------------

    if not os.path.exists(DB_FILE):
        raise HTTPException(status_code=404, detail="Base de données vide")

    with open(DB_FILE, "r") as f:
        for line in f:
            try:
                product = json.loads(line.strip())
                if product['id'] == product_id:
                    return product
            except json.JSONDecodeError:
                continue
                
    raise HTTPException(status_code=404, detail="Produit non trouvé")
