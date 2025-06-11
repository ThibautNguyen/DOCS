# Guide d'Authentification pour les Applications Streamlit

## Contexte
Ce guide documente les bonnes pratiques et solutions pour l'authentification dans les applications Streamlit, basé sur l'expérience acquise lors du développement de plusieurs applications.

> Pour une implémentation technique détaillée, consultez le [guide d'implémentation Streamlit](streamlit_auth_guide.md).

## Points d'attention importants

### 1. Choix de la bibliothèque
- **streamlit-authenticator** version 0.3.2 est recommandée
- **Ne pas utiliser** la version 0.4.2 car elle :
  - Change la signature de la méthode `login()`
  - Modifie la structure attendue du YAML
  - N'est pas compatible avec le code existant

### 2. Environnement virtuel
- Toujours utiliser un environnement virtuel dédié
- Activer l'environnement avant toute installation :
  ```powershell
  .\.venv\Scripts\Activate.ps1  # Windows
  source .venv/bin/activate     # Linux/Mac
  ```
- Vérifier l'installation :
  ```powershell
  pip list | findstr streamlit-authenticator
  ```

### 3. Génération de hash
- La version 0.3.2 n'inclut pas de méthode `Hasher`
- Utiliser bcrypt directement :
  ```python
  import bcrypt
  password = b'votre_mot_de_passe'
  hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
  print(hash.decode())
  ```
  > Voir le [guide d'implémentation](streamlit_auth_guide.md#génération-de-hash-de-mot-de-passe) pour plus de détails.

### 4. Structure du YAML
- Format exact requis :
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
  > Consultez le [guide d'implémentation](streamlit_auth_guide.md#1-configuration-configyaml) pour des exemples complets.

## Dépannage courant

### 1. Module non trouvé
- Vérifier l'activation de l'environnement virtuel
- Vérifier l'installation : `pip install streamlit-authenticator==0.3.2`

### 2. Erreur de hash
- Vérifier que le hash est au format bcrypt
- Vérifier que le mot de passe correspond exactement

### 3. Erreur de structure YAML
- Vérifier l'indentation
- Vérifier la présence de tous les champs requis

## Historique des problèmes résolus

1. **Problème de versions multiples**
   - Solution : Utiliser strictement la version 0.3.2
   - Raison : Compatibilité avec le code existant

2. **Problème d'environnement virtuel**
   - Solution : Utiliser un environnement virtuel dédié
   - Raison : Isolation des dépendances

3. **Problème de génération de hash**
   - Solution : Utiliser bcrypt directement
   - Raison : Absence de `Hasher` en 0.3.2

4. **Problème de structure YAML**
   - Solution : Suivre exactement la structure documentée
   - Raison : Format strict requis par 0.3.2

## Bonnes pratiques

1. **Sécurité**
   - Ne jamais stocker les mots de passe en clair
   - Utiliser des clés de cookie uniques par application
   - Limiter la durée de validité des cookies

2. **Maintenance**
   - Documenter les changements de configuration
   - Garder une trace des hash générés
   - Maintenir une liste des utilisateurs autorisés

3. **Développement**
   - Tester l'authentification dans un environnement isolé
   - Vérifier la compatibilité des versions
   - Documenter les dépendances dans requirements.txt

> Retour à la [documentation principale](../README.md) 