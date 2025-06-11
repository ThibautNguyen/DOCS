# Design System - Standards de Design des Applications

## Table des Matières
1. [Palettes de Couleurs Thématiques](#1-palettes-de-couleurs-thématiques)
2. [Usage des Couleurs](#2-usage-des-couleurs)
3. [Typographie et Texte](#3-typographie-et-texte)

## 1. Palettes de Couleurs Thématiques

Chaque thématique possède sa propre palette de couleurs, avec une couleur dominante et des variations. Ces palettes sont conçues pour assurer une cohérence visuelle à travers toutes les applications.

### Population
- Dominante : `#3e7256`
- Variations : `#e3f7ec`, `#97c1ab`, `#3B825C`, `#3e7256`, `#083d20`

### Logement
- Dominante : `#252A57`
- Variations : `#c5d7ff`, `#9aabd9`, `#5C70BD`, `#464FA2`

### Environnement
- Dominante : `#518C52`
- Variations : `#D1FFCD`, `#A3E3A4`, `#5BC465`, `#518C52`, `#325733`

### Éducation
- Dominante : `#784887`
- Variations : `#F4E5FB`, `#CEB4DB`, `#B166D4`, `#784887`, `#42264F`

### Énergie
- Dominante : `#7BA23A`
- Variations : `#D4FF9D`, `#A0D34B`, `#485E22`, `#0A3004`

### Économie
- Dominante : `#B8A623`
- Variations : `#fff1ae`, `#DED181`, `#D9C42A`, `#B8A623`, `#8A7D1A`, `#5C5311`

### Finances locales
- Dominante : `#F99B27`

### Mobilité
- Dominante : `#4C97BA`
- Variations : `#B1E3EF`, `#68BFE5`, `#276D8E`, `#2A4F5E`, `#2A4F5E`

### Santé & Social
- Dominante : `#F0A4C3`

### Vie citoyenne
- Dominante : `#F36A76`

### Sécurité
- Dominante : `#727DA0`

## 2. Usage des Couleurs

### Cartes Choroplèthes
Pour les cartes choroplèthes, utiliser la couleur dominante comme point de référence et créer un dégradé en ajustant la luminosité :
- Les valeurs les plus élevées utilisent la couleur dominante
- Les valeurs intermédiaires utilisent des variations plus claires
- Les valeurs les plus basses utilisent les variations les plus claires
- Pour les données manquantes, utiliser un gris neutre (`#CCCCCC`)

### Graphiques et Visualisations
- Utiliser la couleur dominante pour mettre en évidence les informations principales
- Les variations peuvent être utilisées pour les données secondaires ou les comparaisons
- Maintenir un contraste suffisant pour garantir la lisibilité

### Accessibilité
- S'assurer que les combinaisons de couleurs respectent les normes d'accessibilité WCAG 2.1
- Prévoir des alternatives pour les utilisateurs daltoniens
- Ne pas utiliser la couleur comme seul moyen de transmission d'information

## 3. Typographie et Texte

### Blocs de Texte
- **Police :** OpenSans
- **Couleur dominante :** `#272F4D`
- Utilisation : Pour tout le contenu textuel général de l'application (paragraphes, descriptions, labels, etc.)

### Datavisualisations
- **Police :** Axiforma
- **Couleur dominante :** `#000000`
- Utilisation : Pour tous les éléments textuels dans :
  - Cartographies
  - Graphiques
  - Tableaux
  - Autres visualisations de données

### Hiérarchie Typographique
Pour maintenir une hiérarchie visuelle cohérente :
- Titres : OpenSans Bold
- Sous-titres : OpenSans SemiBold
- Corps de texte : OpenSans Regular
- Notes et légendes : OpenSans Light

Pour les datavisualisations :
- Titres de graphiques : Axiforma Bold
- Labels d'axes : Axiforma Regular
- Légendes : Axiforma Light 