# Guide d'Implémentation de l'Authentification Streamlit

## Introduction
Ce guide fournit des instructions détaillées pour implémenter l'authentification dans une application Streamlit en utilisant `streamlit-authenticator`.

## Prérequis

### 1. Dépendances
```txt
streamlit-authenticator==0.3.2
bcrypt>=3.1.7
PyYAML>=5.3.1
```

### 2. Structure des fichiers
```
votre_app/
├── .venv/                  # Environnement virtuel
├── config.yaml            # Configuration d'authentification
├── requirements.txt       # Dépendances
└── app.py                # Application Streamlit
```

## Implémentation

### 1. Configuration (config.yaml)
```yaml
credentials:
  usernames:
    username:
      email: email@example.com
      name: Nom Utilisateur
      password: $2b$12$...  # Hash bcrypt
cookie:
  expiry_days: 30
  key: some_signature_key
  name: some_cookie_name
preauthorized:
  emails:
    - email@example.com
```

### 2. Code d'authentification (app.py)
```python
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Charger la configuration
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Créer l'authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Interface de connexion
name, authentication_status, username = authenticator.login('Login', 'main')

# Gestion de l'authentification
if authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
elif authentication_status:
    # Contenu de l'application
    st.write(f'Welcome *{name}*')
    authenticator.logout('Logout', 'main')
```

## Génération de hash de mot de passe

### 1. Script de génération (generate_hash.py)
```python
import bcrypt

def generate_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

# Exemple d'utilisation
password = 'votre_mot_de_passe'
hash = generate_hash(password)
print(f'Hash pour {password}: {hash}')
```

### 2. Utilisation
```bash
python generate_hash.py
```

## Dépannage

### 1. Erreurs courantes
- **ModuleNotFoundError**: Vérifier l'installation dans le bon environnement virtuel
- **YAMLError**: Vérifier la structure et l'indentation du YAML
- **AuthenticationError**: Vérifier le hash et le mot de passe

### 2. Vérifications
- Environnement virtuel activé
- Version correcte de streamlit-authenticator
- Structure YAML valide
- Hash bcrypt correct

## Bonnes pratiques

### 1. Sécurité
- Utiliser des mots de passe forts
- Changer régulièrement les clés de cookie
- Limiter les tentatives de connexion

### 2. Maintenance
- Documenter les changements de configuration
- Sauvegarder les hash générés
- Maintenir une liste des utilisateurs

### 3. Développement
- Tester dans un environnement isolé
- Vérifier la compatibilité des versions
- Documenter les dépendances 