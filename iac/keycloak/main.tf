terraform {
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = ">= 4.0.0"
    }
  }
}

# Configuration du Provider (Connexion à ton Keycloak)
provider "keycloak" {
  client_id     = "admin-cli"
  username      = "admin"
  password      = "De181mVOXDmewD1JK0D3"
  # Attention : On utilise ton URL publique DDNS avec /auth
  url           = "https://devsecopslab.ddns.net/auth"
}

# =======================================================
# 1. CRÉATION DU REALM
# =======================================================
resource "keycloak_realm" "realm" {
  realm   = "devsecops"
  enabled = true
  display_name = "DevSecOps Lab Realm"
}

# =======================================================
# 2. CRÉATION DU CLIENT "myclient"
# =======================================================
resource "keycloak_openid_client" "myclient" {
  realm_id  = keycloak_realm.realm.id
  client_id = "myclient"
  name      = "My App Client"
  enabled   = true

  access_type           = "PUBLIC" # Car c'est pour un frontend SPA/Web
  standard_flow_enabled = true     # Login via page web
  direct_access_grants_enabled = true # Login via API (user/pass)

  # Pour le lab, on autorise tout. En prod, mettre les URLs précises.
  valid_redirect_uris = ["*"]
  web_origins         = ["*"]
}

# =======================================================
# 3. CRÉATION DES RÔLES
# =======================================================
resource "keycloak_role" "writer_role" {
  realm_id = keycloak_realm.realm.id
  name     = "writer"
  description = "Role pour l'ecriture"
}

resource "keycloak_role" "reader_role" {
  realm_id = keycloak_realm.realm.id
  name     = "reader"
  description = "Role pour la lecture seule"
}

# =======================================================
# 4. CRÉATION DES UTILISATEURS
# =======================================================

# --- User 1 (Sera Writer) ---
resource "keycloak_user" "user1" {
  realm_id   = keycloak_realm.realm.id
  username   = "user1"
  enabled    = true
  email      = "user1@devsecops.local"
  email_verified = true
  first_name = "Alice"
  last_name  = "Writer"

  initial_password {
    value     = "1234"
    temporary = false
  }
}

# --- User 2 (Sera Reader) ---
resource "keycloak_user" "user2_r" {
  realm_id   = keycloak_realm.realm.id
  username   = "user2_r"
  enabled    = true
  email      = "user2@devsecops.local"
  email_verified = true
  first_name = "Bob"
  last_name  = "Reader"

  initial_password {
    value     = "1234"
    temporary = false
  }
}

# =======================================================
# 5. ASSIGNATION DES RÔLES
# =======================================================

# Lier User1 -> Writer
resource "keycloak_user_roles" "user1_roles" {
  realm_id = keycloak_realm.realm.id
  user_id  = keycloak_user.user1.id

  role_ids = [
    keycloak_role.writer_role.id
  ]
}

# Lier User2_r -> Reader
resource "keycloak_user_roles" "user2_roles" {
  realm_id = keycloak_realm.realm.id
  user_id  = keycloak_user.user2_r.id

  role_ids = [
    keycloak_role.reader_role.id
  ]
}
