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
PUBLIC_KEY_STR = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxi+al0SFUZoNWixwMgJL5XzjQ7ABa77qKb4SBBswD75RghsRZlOsajRj6/Zt+euMacokc7+Q+7EYLfXknAgHP+dQHNzug/rnV/lzQXya/F7xUZNYhoaX+xSIK/y7OoawJkqgdKIX6WKKQChAvJa3KZuyHum6WBGg6thKm4PjjzDwkzpPY2zpRKDaY9gurgZZ2feHa2ps9TKa0p9mtVKvzAxFApwx2nR24/kQBdKYRBkj71hgiavZmhZi4zTBkmNVV0Ckn4hJKac8PjZQthVjJTADgmTCH3vhsMkdFvNLIh2q5b5pYXJ+okAciv29kSOLECM3cS3VBb5mbLo1LYtwkQIDAQAB" 

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
