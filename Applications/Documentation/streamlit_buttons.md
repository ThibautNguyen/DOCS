# Guide d'Harmonisation des Boutons Streamlit

## Problématique rencontrée

- Par défaut, **la couleur des boutons Streamlit dépend de l'ordre d'apparition** sur la page (bleu, vert, blanc, etc.).
- Ce comportement s'applique aussi dans la sidebar : le premier bouton est bleu, le second vert, le troisième blanc, etc.
- Il est **impossible de cibler un bouton par son texte** de façon fiable avec du CSS natif Streamlit (les sélecteurs avancés comme `:has()` ou `:contains()` ne sont pas toujours supportés).
- Les classes CSS générées par Streamlit sont dynamiques et non documentées.

## Bonnes pratiques pour l'uniformité

1. **Si tu veux une couleur précise pour un bouton dans la sidebar (ex : blanc pour "Déconnexion") sur toutes les pages :**
   - Applique ce CSS dans la sidebar :

```python
st.markdown(
    '''
    <style>
    section[data-testid="stSidebar"] button {
        background-color: #fff !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #f5f5f5 !important;
        color: #111 !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)
```
- **Ce CSS force la couleur blanche sur tous les boutons de la sidebar**, garantissant un rendu uniforme, quel que soit l'ordre ou le nombre de boutons.

2. **Si tu veux la couleur "primaire" (bleu) Streamlit :**
   - Place le bouton en premier dans la sidebar (avant tout autre bouton).
   - Attention : ce n'est pas fiable si d'autres boutons sont ajoutés dynamiquement.

3. **Pour une couleur différente (rouge, vert, etc.)**
   - Modifie le CSS ci-dessus en changeant `background-color` et `color`.

## À éviter
- Ne pas compter sur l'ordre d'apparition pour l'uniformité si l'application évolue.
- Ne pas utiliser de sélecteurs CSS avancés (`:has()`, `:contains()`) : non supportés partout.
- Ne pas cibler les classes générées par Streamlit (elles changent à chaque build).

## Exemple d'intégration dans un module utilitaire

```python
def bouton_deconnexion():
    with st.sidebar:
        st.markdown('''
            <style>
            section[data-testid="stSidebar"] button {
                background-color: #fff !important;
                color: #333 !important;
                border: 1px solid #ddd !important;
                font-weight: 600;
            }
            section[data-testid="stSidebar"] button:hover {
                background-color: #f5f5f5 !important;
                color: #111 !important;
            }
            </style>
        ''', unsafe_allow_html=True)
        if st.button('🚪 Déconnexion', use_container_width=True):
            # ... logique de déconnexion ...
            pass
```

## Résumé
- **Pour garantir l'uniformité des boutons Streamlit sur toutes les pages, injecte un CSS ciblant la sidebar.**
- **Documente ce choix dans le design system du projet.**
- **Teste le rendu sur plusieurs pages pour vérifier l'effet global.** 