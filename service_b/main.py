from fastapi.middleware.cors import CORSMiddleware
# 1. Import de APIRouter
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
import json
import os
from jose import JWTError, jwt

app = FastAPI()

# --- BLOC CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CRÉATION DU ROUTER AVEC LE PRÉFIXE
# C'est la ligne magique pour que l'Ingress trouve la route
router = APIRouter(prefix="/service-b")

# --- CONFIGURATION SÉCURITÉ ---
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

# Configuration du chemin vers les données (Volume partagé)
DB_FILE = "/data/products.txt"

# 3. DÉFINITION DE LA ROUTE SUR LE ROUTER (et non plus sur app)
@router.get("/products/{product_id}")
def get_product(product_id: str, token: dict = Depends(verify_token)):
    # --- VÉRIFICATION RBAC ---
    roles = token.get("realm_access", {}).get("roles", [])
    
    # On vérifie si le rôle "reader" est présent
    if "reader" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé : Vous n'avez pas le rôle 'reader'."
        )
    # -------------------------

    if not os.path.exists(DB_FILE):
        raise HTTPException(status_code=404, detail="Base de données vide (Aucun produit n'a été créé).")

    try:
        with open(DB_FILE, "r") as f:
            for line in f:
                try:
                    product = json.loads(line.strip())
                    # Comparaison robuste (string vs string) pour éviter les erreurs de type
                    if str(product.get('id')) == str(product_id):
                        return product
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur technique lors de la lecture: {str(e)}")
                
    raise HTTPException(status_code=404, detail="Produit non trouvé")

# 4. INCLUSION DU ROUTER DANS L'APPLICATION PRINCIPALE
app.include_router(router)
