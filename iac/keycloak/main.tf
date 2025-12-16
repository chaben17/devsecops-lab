terraform {
  required_providers {
    keycloak = {
      source  = "mrparkers/keycloak"
      version = ">= 4.0.0"
    }
  }
  # On garde le backend Kubernetes pour que ton GitHub Actions fonctionne
  backend "kubernetes" {
    secret_suffix    = "state"
    config_path      = "~/.kube/config"
    namespace        = "default"
  }
}

# --- VARIABLES ---
variable "keycloak_password" {
  type      = string
  sensitive = true
}

variable "keycloak_url" {
  type    = string
  default = "http://localhost:8080"
}

# --- PROVIDER ---
provider "keycloak" {
  client_id     = "admin-cli"
  username      = "admin"
  password      = var.keycloak_password
  url           = var.keycloak_url
}

# --- 1. REALM ---
resource "keycloak_realm" "devsecops_realm" {
  realm        = "devsecops"
  enabled      = true
  display_name = "DevSecOps Lab Realm"
}

# --- 2. CLIENT ---
resource "keycloak_openid_client" "webapp_client" {
  realm_id  = keycloak_realm.devsecops_realm.id
  client_id = "myclient"

  name    = "My Client App"
  enabled = true

  access_type                  = "PUBLIC"
  standard_flow_enabled        = true
  direct_access_grants_enabled = true

  valid_redirect_uris = [
    "http://devsecops.local/*",
    "http://localhost:8080/*"
  ]
  web_origins = ["+"]
}

# --- 3. ROLES ---
resource "keycloak_role" "role_reader" {
  realm_id    = keycloak_realm.devsecops_realm.id
  name        = "reader"
  description = "Role lecture seule"
}

resource "keycloak_role" "role_writer" {
  realm_id    = keycloak_realm.devsecops_realm.id
  name        = "writer"
  description = "Role ecriture"
}

# --- 4. UTILISATEURS ---

# User A (sera Writer)
resource "keycloak_user" "user_a" {
  realm_id = keycloak_realm.devsecops_realm.id
  username = "user_a"
  enabled  = true

  email      = "usera@devsecops.local"
  first_name = "User"
  last_name  = "A"

  initial_password {
    value     = "1234"
    temporary = false
  }
}

# User B (sera Reader)
resource "keycloak_user" "user_b" {
  realm_id = keycloak_realm.devsecops_realm.id
  username = "user_b"
  enabled  = true

  email      = "userb@devsecops.local"
  first_name = "User"
  last_name  = "B"

  initial_password {
    value     = "1234"
    temporary = false
  }
}

# --- 5. ASSIGNATION DES ROLES ---

# User A -> Writer
resource "keycloak_user_roles" "user_a_roles" {
  realm_id = keycloak_realm.devsecops_realm.id
  user_id  = keycloak_user.user_a.id

  role_ids = [
    keycloak_role.role_writer.id
  ]
}

# User B -> Reader
resource "keycloak_user_roles" "user_b_roles" {
  realm_id = keycloak_realm.devsecops_realm.id
  user_id  = keycloak_user.user_b.id

  role_ids = [
    keycloak_role.role_reader.id
  ]
}
