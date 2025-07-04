#!/usr/bin/env python3
"""
Script intelligent pour créer les dictionnaires des variables des données d'accidents corporels
Gère automatiquement les guillemets pour les correspondances multiples
"""

import csv
import os
import re

def format_correspondances(correspondances):
    """
    Formate automatiquement les correspondances de codes.
    Ajoute des guillemets si la chaîne contient plusieurs valeurs séparées par des tirets.
    Remplace les tirets cadratins par des deux-points et les points-virgules par des barres verticales.
    """
    # Remplacer les tirets cadratins par des deux-points
    correspondances_cleaned = correspondances.replace(' – ', ': ')
    
    # Remplacer les points-virgules par des barres verticales
    correspondances_cleaned = correspondances_cleaned.replace('; ', ' | ')
    
    # Détecter les correspondances multiples (plus d'un deux-points maintenant)
    if ': ' in correspondances_cleaned and correspondances_cleaned.count(': ') > 1:
        return f'"{correspondances_cleaned}"'
    return correspondances_cleaned

def get_regroupements_simplifies():
    """
    Retourne les regroupements simplifiés pour les variables avec beaucoup de codes.
    """
    regroupements = {
        'catv': {
            'Vélo et VAE': ['01', '80'],
            '2 roues motorisé': ['02', '04', '05', '06', '30', '31', '32', '33', '34', '35', '36', '41', '42', '43'],
            'Voiture ou véhicule utilitaires léger': ['07', '08', '09', '10', '11', '12'],
            'Poids lourd': ['13', '14', '15', '16', '17', '20'],
            'Tracteur agricole': ['21'],
            'Autobus et autocar': ['18', '37', '38'],
            'Train et tramway': ['19', '39', '40'],
            'Trottinette': ['50', '60'],
            'Autre': ['00', '03', '99']
        },
        'manv': {
            'Circulation normale': ['1', '2'],
            'Changement de file': ['3', '11', '12'],
            'Déportement': ['13', '14'],
            'Virage': ['15', '16'],
            'Dépassement': ['17', '18'],
            'Manœuvres spéciales': ['4', '5', '6', '10', '19', '20', '21'],
            'Circulation particulière': ['7', '8', '9', '22', '25'],
            'Stationnement/Arrêt': ['23', '24', '26'],
            'Non renseigné': ['-1', '0']
        },
        'obs': {
            'Véhicule/Infrastructure': ['1', '6'],
            'Végétation': ['2'],
            'Glissière/Barrière': ['3', '4', '5', '11'],
            'Signalisation/Poteau': ['7', '8'],
            'Mobilier urbain': ['9', '10', '12'],
            'Terrain naturel': ['13', '14', '15', '16', '17'],
            'Sans objet/Non renseigné': ['-1', '0']
        },
        'secu1': {
            'Aucun équipement': ['-1', '0', '8'],
            'Protection corps': ['1', '3'],
            'Protection tête': ['2'],
            'Équipement 2RM': ['5', '6', '7'],
            'Visibilité/Autre': ['4', '9']
        },
        'secu2': {
            'Aucun équipement': ['-1', '0', '8'],
            'Protection corps': ['1', '3'],
            'Protection tête': ['2'],
            'Équipement 2RM': ['5', '6', '7'],
            'Visibilité/Autre': ['4', '9']
        },
        'secu3': {
            'Aucun équipement': ['-1', '0', '8'],
            'Protection corps': ['1', '3'],
            'Protection tête': ['2'],
            'Équipement 2RM': ['5', '6', '7'],
            'Visibilité/Autre': ['4', '9']
        }
    }
    return regroupements

def creer_correspondances_simplifiees(variable_name, correspondances_detaillees):
    """
    Crée les correspondances simplifiées pour une variable donnée.
    Utilise des barres verticales comme séparateur pour la compatibilité Excel.
    """
    regroupements = get_regroupements_simplifies()
    
    if variable_name not in regroupements:
        return correspondances_detaillees
    
    groupes = regroupements[variable_name]
    correspondances_simplifiees = []
    
    for groupe_nom, codes in groupes.items():
        correspondances_simplifiees.append(f"{', '.join(codes)}: {groupe_nom}")
    
    result = ' | '.join(correspondances_simplifiees)
    
    # Ajouter des guillemets si nécessaire
    if ' | ' in result:
        return f'"{result}"'
    return result

def get_variable_definitions():
    """Retourne les définitions complètes des variables pour chaque table."""
    
    definitions = {
        'caract': {
            'Num_Acc': ('Numéro d\'identifiant de l\'accident', 'Identifiant unique alphanumérique'),
            'jour': ('Jour de l\'accident', 'Jour de l\'accident'),
            'mois': ('Mois de l\'accident', 'Mois de l\'accident'),
            'an': ('Année de l\'accident', 'Année de l\'accident'),
            'hrmn': ('Heure et minutes de l\'accident', 'Heure et minutes de l\'accident'),
            'lum': ('Lumière : conditions d\'éclairage dans lesquelles l\'accident s\'est produit', '1 – Plein jour; 2 – Crépuscule ou aube; 3 – Nuit sans éclairage public; 4 – Nuit avec éclairage public non allumé; 5 – Nuit avec éclairage public allumé'),
            'dep': ('Département : Code INSEE du département', 'Code INSEE du département suivi d\'un 0 (sauf 02A et 02B)'),
            'com': ('Commune : Le numéro de commune est un code donné par l\'INSEE', 'Code INSEE de la commune'),
            'agg': ('Localisation', '1 – Hors agglomération; 2 – En agglomération'),
            'int': ('Intersection', '1 – Hors intersection; 2 – Intersection en X; 3 – Intersection en T; 4 – Intersection en Y; 5 – Intersection à plus de 4 branches; 6 – Giratoire; 7 – Place; 8 – Passage à niveau; 9 – Autre intersection'),
            'atm': ('Conditions atmosphériques', '-1 – Non renseigné; 1 – Normale; 2 – Pluie légère; 3 – Pluie forte; 4 – Neige - grêle; 5 – Brouillard - fumée; 6 – Vent fort - tempête; 7 – Temps éblouissant; 8 – Temps couvert; 9 – Autre'),
            'col': ('Type de collision', '-1 – Non renseigné; 1 – Deux véhicules - frontale; 2 – Deux véhicules – par l\'arrière; 3 – Deux véhicules – par le côté; 4 – Trois véhicules et plus – en chaîne; 5 – Trois véhicules et plus - collisions multiples; 6 – Autre collision; 7 – Sans collision'),
            'adr': ('Adresse sommaire non normalisée', 'En principe inutile si l\'adresse normalisée est correctement renseignée'),
            'lat': ('Latitude', 'Latitude'),
            'long': ('Longitude', 'Longitude'),
            'gps': ('Zone géographique', 'M – Métropole; A – Antilles (Martinique ou Guadeloupe); G – Guyane; R – Réunion; S – St Pierre et Miquelon; Y – Mayotte; P – Polynésie française; W – Wallis et Futuna; C – Nouvelle Calédonie; T – Terres austr. et antarct. Françaises'),
            'org': ('Organisme', '1 – Gendarmerie; 2 – Préfecture de Police de Paris; 3 – C.R.S.; 4 – P.A.F.; 5 – Sécurité publique'),
            'type_numero': ('Type de numéro', '0 – Numéro non renseigné; 1 – Adresse postale; 2 – Candélabre (quand on se rattache à un candélabre répertorié dans une base de données urbaine); 9 – Autre'),
            'numero': ('Numéro de l\'adresse ou du candélabre', 'Peut contenir bis, ter...'),
            'distancemetre': ('Distance au numéro', 'blancs si non renseigné'),
            'libellevoie': ('Libellé de la voie', 'Libellé de la voie'),
            'coderivoli': ('code rivoli', 'Cf. cadastre'),
            'grav': ('Indice de gravité de l\'accident', 'Calculé selon le coût normalisé des atteintes aux victimes, par application des valeurs tutélaires 2010 (un tué vaut 100, un hospitalisé vaut 10,8, un blessé léger vaut 0,44).'),
            'tue': ('Nombre de personnes tuées dans l\'accident', 'Nombre de personnes tuées dans l\'accident'),
            'tbg': ('Nombre de blessés hospitalisés ("blessés graves") dans l\'accident', 'Nombre de blessés hospitalisés ("blessés graves") dans l\'accident'),
            'tbl': ('Nombre de blessés légers dans l\'accident', 'Nombre de blessés légers dans l\'accident'),
            'tindm': ('Nombre de personnes indemnes dans l\'accident', 'Nombre de personnes indemnes dans l\'accident')
        },
        
        'lieux': {
            'Num_Acc': ('Identifiant de l\'accident identique à celui du fichier "rubrique CARACTERISTIQUES" repris dans l\'accident', 'Identifiant unique alphanumérique'),
            'catr': ('Catégorie de route', '1 – Autoroute; 2 – Route nationale; 3 – Route Départementale; 4 – Voie Communales; 5 – Hors réseau public; 6 – Parc de stationnement ouvert à la circulation publique; 7 – Routes de métropole urbaine; 9 – autre'),
            'voie': ('Numéro de la route', 'Numéro de la route'),
            'v1': ('Indice numérique du numéro de route', 'exemple : 2 bis, 3 ter etc.'),
            'v2': ('Lettre indice alphanumérique de la route', 'Lettre indice alphanumérique de la route'),
            'circ': ('Régime de circulation', '-1 – Non renseigné; 1 – A sens unique; 2 – Bidirectionnelle; 3 – A chaussées séparées; 4 – Avec voies d\'affectation variable'),
            'nbv': ('Nombre total de voies de circulation', 'Nombre total de voies de circulation'),
            'vosp': ('Signale l\'existence d\'une voie réservée, indépendamment du fait que l\'accident ait lieu ou non sur cette voie', '-1 – Non renseigné; 0 – Sans objet; 1 – Piste cyclable; 2 – Bande cyclable; 3 – Voie réservée'),
            'prof': ('Profil en long décrit la déclivité de la route à l\'endroit de l\'accident', '-1 – Non renseigné; 1 – Plat; 2 – Pente; 3 – Sommet de côte; 4 – Bas de côte'),
            'pr': ('Numéro du PR de rattachement (numéro de la borne amont)', 'La valeur -1 signifie que le PR n\'est pas renseigné'),
            'pr1': ('Distance en mètres au PR (par rapport à la borne amont)', 'La valeur -1 signifie que le PR n\'est pas renseigné'),
            'plan': ('Tracé en plan', '-1 – Non renseigné; 1 – Partie rectiligne; 2 – En courbe à gauche; 3 – En courbe à droite; 4 – En « S »'),
            'lartpc': ('Largeur du terre-plein central (TPC) s\'il existe', 'en m'),
            'larrout': ('Largeur de la chaussée affectée à la circulation des véhicules ne sont pas compris les bandes d\'arrêt d\'urgence, les TPC et les places de stationnement', 'en m'),
            'surf': ('État de la surface', '-1 – Non renseigné; 1 – Normale; 2 – Mouillée; 3 – Flaques; 4 – Inondée; 5 – Enneigée; 6 – Boue; 7 – Verglacée; 8 – Corps gras – huile; 9 – Autre'),
            'infra': ('Aménagement - Infrastructure', '-1 – Non renseigné; 0 – Aucun; 1 – Souterrain - tunnel; 2 – Pont - autopont; 3 – Bretelle d\'échangeur ou de raccordement; 4 – Voie ferrée; 5 – Carrefour aménagé; 6 – Zone piétonne; 7 – Zone de péage; 8 – Chantier; 9 – Autres'),
            'situ': ('Situation de l\'accident', '-1 – Non renseigné; 0 – Aucun; 1 – Sur chaussée; 2 – Sur bande d\'arrêt d\'urgence; 3 – Sur accotement; 4 – Sur trottoir; 5 – Sur piste cyclable; 6 – Sur autre voie spéciale; 8 – Autres'),
            'vma': ('Vitesse maximale autorisée sur le lieu et au moment de l\'accident', 'Vitesse maximale autorisée sur le lieu et au moment de l\'accident'),
            'env1': ('Point école', 'Proximité d\'une école')
        },
        
        'vehicules': {
            'Num_Acc': ('Identifiant de l\'accident identique à celui du fichier "rubrique CARACTERISTIQUES" repris pour chacun des véhicules décrits impliqués dans l\'accident', 'Identifiant unique alphanumérique'),
            'id_vehicule': ('Identifiant unique du véhicule repris pour chacun des usagers occupant ce véhicule (y compris les piétons qui sont rattachés aux véhicules qui les ont heurtés)', 'Code numérique'),
            'num_veh': ('Identifiant du véhicule repris pour chacun des usagers occupant ce véhicule (y compris les piétons qui sont rattachés aux véhicules qui les ont heurtés)', 'Code alphanumérique'),
            'senc': ('Sens de circulation', '-1 – Non renseigné; 0 – Inconnu; 1 – PK ou numéro d\'adresse postale croissant; 2 – PK ou PR ou numéro d\'adresse postale décroissant; 3 – Absence de repère'),
            'catv': ('Catégorie du véhicule', '00 – Indéterminable; 01 – Bicyclette; 02 – Cyclomoteur <50cm3; 03 – Voiturette (Quadricycle à moteur carrossé) (anciennement "voiturette ou tricycle à moteur"); 04 – Référence inutilisée depuis 2006 (scooter immatriculé); 05 – Référence inutilisée depuis 2006 (motocyclette); 06 – Référence inutilisée depuis 2006 (side-car); 07 – VL seul; 08 – Référence inutilisée depuis 2006 (VL + caravane); 09 – Référence inutilisée depuis 2006 (VL + remorque); 10 – VU seul 1,5T <= PTAC <= 3,5T avec ou sans remorque (anciennement VU seul 1,5T <= PTAC <= 3,5T); 11 – Référence inutilisée depuis 2006 (VU (10) + caravane); 12 – Référence inutilisée depuis 2006 (VU (10) + remorque); 13 – PL seul 3,5T <PTCA <= 7,5T; 14 – PL seul > 7,5T; 15 – PL > 3,5T + remorque; 16 – Tracteur routier seul; 17 – Tracteur routier + semi-remorque; 18 – Référence inutilisée depuis 2006 (transport en commun); 19 – Référence inutilisée depuis 2006 (tramway); 20 – Engin spécial; 21 – Tracteur agricole; 30 – Scooter < 50 cm3; 31 – Motocyclette > 50 cm3 et <= 125 cm3; 32 – Scooter > 50 cm3 et <= 125 cm3; 33 – Motocyclette > 125 cm3; 34 – Scooter > 125 cm3; 35 – Quad léger <= 50 cm3 (Quadricycle à moteur non carrossé); 36 – Quad lourd > 50 cm3 (Quadricycle à moteur non carrossé); 37 – Autobus; 38 – Autocar; 39 – Train; 40 – Tramway; 41 – 3RM <= 50 cm3; 42 – 3RM > 50 cm3 <= 125 cm3; 43 – 3RM > 125 cm3; 50 – EDP à moteur; 60 – EDP sans moteur; 80 – VAE; 99 – Autre véhicule'),
            'obs': ('Obstacle fixe heurté', '-1 – Non renseigné; 0 – Sans objet; 1 – Véhicule en stationnement; 2 – Arbre; 3 – Glissière métallique; 4 – Glissière béton; 5 – Autre glissière; 6 – Bâtiment, mur, pile de pont; 7 – Support de signalisation verticale ou poste d\'appel d\'urgence; 8 – Poteau; 9 – Mobilier urbain; 10 – Parapet; 11 – Ilot, refuge, borne haute; 12 – Bordure de trottoir; 13 – Fossé, talus, paroi rocheuse; 14 – Autre obstacle fixe sur chaussée; 15 – Autre obstacle fixe sur trottoir ou accotement; 16 – Sortie de chaussée sans obstacle; 17 – Buse – tête d\'aqueduc'),
            'obsm': ('Obstacle mobile heurté', '-1 – Non renseigné; 0 – Aucun; 1 – Piéton; 2 – Véhicule; 4 – Véhicule sur rail; 5 – Animal domestique; 6 – Animal sauvage; 9 – Autre'),
            'choc': ('Point de choc initial', '-1 – Non renseigné; 0 – Aucun; 1 – Avant; 2 – Avant droit; 3 – Avant gauche; 4 – Arrière; 5 – Arrière droit; 6 – Arrière gauche; 7 – Côté droit; 8 – Côté gauche; 9 – Chocs multiples (tonneaux)'),
            'manv': ('Manœuvre principale avant l\'accident', '-1 – Non renseigné; 0 – Inconnue; 1 – Sans changement de direction; 2 – Même sens, même file; 3 – Entre 2 files; 4 – En marche arrière; 5 – A contresens; 6 – En franchissant le terre-plein central; 7 – Dans le couloir bus, dans le même sens; 8 – Dans le couloir bus, dans le sens inverse; 9 – En s\'insérant; 10 – En faisant demi-tour sur la chaussée; 11 – Changeant de file A gauche; 12 – Changeant de file A droite; 13 – Déporté A gauche; 14 – Déporté A droite; 15 – Tournant A gauche; 16 – Tournant A droite; 17 – Dépassant A gauche; 18 – Dépassant A droite; 19 – Traversant la chaussée; 20 – Manœuvre de stationnement; 21 – Manœuvre d\'évitement; 22 – Ouverture de porte; 23 – Arrêté (hors stationnement); 24 – En stationnement (avec occupants); 25 – Circulant sur trottoir; 26 – Autres manœuvres'),
            'motor': ('Type de motorisation du véhicule', '-1 – Non renseigné; 0 – Inconnue; 1 – Hydrocarbures; 2 – Hybride électrique; 3 – Electrique; 4 – Hydrogène; 5 – Humaine; 6 – Autre'),
            'occutc': ('Nombre d\'occupants dans le transport en commun', 'Nombre d\'occupants dans le transport en commun')
        },
        
        'usagers': {
            'Num_Acc': ('Identifiant de l\'accident identique à celui du fichier "rubrique CARACTERISTIQUES" repris pour chacun des usagers décrits impliqués dans l\'accident', 'Identifiant unique alphanumérique'),
            'id_usager': ('Identifiant unique de l\'usager (y compris les piétons qui sont rattachés aux véhicules qui les ont heurtés)', 'Code numérique'),
            'id_vehicule': ('Identifiant unique du véhicule repris pour chacun des usagers occupant ce véhicule (y compris les piétons qui sont rattachés aux véhicules qui les ont heurtés)', 'Code numérique'),
            'num_veh': ('Identifiant du véhicule repris pour chacun des usagers occupant ce véhicule (y compris les piétons qui sont rattachés aux véhicules qui les ont heurtés)', 'Code alphanumérique'),
            'place': ('Permet de situer la place occupée dans le véhicule par l\'usager au moment de l\'accident', '10 – Piéton (non applicable)'),
            'catu': ('Catégorie d\'usager', '1 – Conducteur; 2 – Passager; 3 – Piéton'),
            'grav': ('Gravité de blessure de l\'usager, les usagers accidentés sont classés en trois catégories de victimes plus les indemnes', '1 – Indemne; 2 – Tué; 3 – Blessé hospitalisé; 4 – Blessé léger'),
            'sexe': ('Sexe de l\'usager', '1 – Masculin; 2 – Féminin'),
            'an_nais': ('Année de naissance de l\'usager', 'Année de naissance de l\'usager'),
            'trajet': ('Motif du déplacement au moment de l\'accident', '-1 – Non renseigné; 0 – Non renseigné; 1 – Domicile – travail; 2 – Domicile – école; 3 – Courses – achats; 4 – Utilisation professionnelle; 5 – Promenade – loisirs; 9 – Autre'),
            'secu': ('Équipement de sécurité - 2 caractères : le premier concerne l\'existence d\'un équipement, le second son utilisation', '"1 – Ceinture | 2 – Casque | 3 – Dispositif enfants | 4 – Équipement réfléchissant | 9 – Autre" pour le 1er caractère; "1 – Oui | 2 – Non | 3 – Non déterminable" pour le 2ème caractère'),
            'secu1': ('Le renseignement du caractère indique la présence et l\'utilisation de l\'équipement de sécurité', '-1 – Non renseigné; 0 – Aucun équipement; 1 – Ceinture; 2 – Casque; 3 – Dispositif enfants; 4 – Gilet réfléchissant; 5 – Airbag (2RM/3RM); 6 – Gants (2RM/3RM); 7 – Gants + Airbag (2RM/3RM); 8 – Non déterminable; 9 – Autre'),
            'secu2': ('Le renseignement du caractère indique la présence et l\'utilisation de l\'équipement de sécurité', '-1 – Non renseigné; 0 – Aucun équipement; 1 – Ceinture; 2 – Casque; 3 – Dispositif enfants; 4 – Gilet réfléchissant; 5 – Airbag (2RM/3RM); 6 – Gants (2RM/3RM); 7 – Gants + Airbag (2RM/3RM); 8 – Non déterminable; 9 – Autre'),
            'secu3': ('Le renseignement du caractère indique la présence et l\'utilisation de l\'équipement de sécurité', '-1 – Non renseigné; 0 – Aucun équipement; 1 – Ceinture; 2 – Casque; 3 – Dispositif enfants; 4 – Gilet réfléchissant; 5 – Airbag (2RM/3RM); 6 – Gants (2RM/3RM); 7 – Gants + Airbag (2RM/3RM); 8 – Non déterminable; 9 – Autre'),
            'locp': ('Localisation du piéton', 'Variable non visible dans les captures fournies'),
            'actp': ('Action du piéton', '-1 – Non renseigné; 0 – Non renseigné ou sans objet; 1 – Sens véhicule heurtant; 2 – Sens inverse du véhicule; 3 – Traversant; 4 – Masqué; 5 – Jouant – courant; 6 – Avec animal; 9 – Autre; A – Monte/descend du véhicule; B – Inconnue'),
            'etatp': ('Cette variable permet de préciser si le piéton accidenté était seul ou non', '-1 – Non renseigné; 1 – Seul; 2 – Accompagné; 3 – En groupe')
        }
    }
    
    return definitions

def read_csv_header(file_path):
    """
    Lire seulement la première ligne (en-tête) d'un fichier CSV.
    Gère différents encodages et formats.
    """
    encodings = ['utf-8', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                # Essayer différents délimiteurs
                for delimiter in [';', ',']:
                    file.seek(0)  # Retourner au début du fichier
                    try:
                        csv_reader = csv.reader(file, delimiter=delimiter)
                        header = next(csv_reader)
                        # Si l'en-tête est une seule chaîne, essayer de la diviser
                        if len(header) == 1:
                            header = header[0].split(delimiter)
                        # Nettoyer les noms de variables
                        header = [var.strip() for var in header]
                        if len(header) > 1:  # S'assurer qu'on a bien séparé les variables
                            return header
                    except:
                        continue
        except Exception as e:
            print(f"Tentative avec {encoding} échouée: {e}")
            continue
    
    print(f"Erreur lecture {file_path}: Impossible de lire l'en-tête avec les encodages disponibles")
    return []

def get_csv_filename(table_name, year):
    """
    Retourne le nom du fichier CSV en fonction de l'année et de la table.
    Gère les différents formats de nommage selon les années.
    """
    # Liste des formats possibles
    formats = [
        # Format 2023 (avec tiret)
        f"{table_name}-{year}.csv",
        f"{table_name}s-{year}.csv",
        f"carcteristiques-{year}.csv",
        # Format 2017-2022 (avec tiret)
        f"{table_name}es-{year}.csv",
        # Format 2005-2016 (avec underscore)
        f"{table_name}_{year}.csv",
        f"{table_name}s_{year}.csv",
        f"caracteristiques_{year}.csv"
    ]
    
    # Tester chaque format
    for fmt in formats:
        if os.path.exists(os.path.join(year, fmt)):
            return fmt
    
    return None

def get_dict_filename(csv_filename):
    """
    Génère le nom du fichier dictionnaire en se basant sur le nom du fichier CSV source.
    Ajoute le préfixe 'dict-' au nom du fichier.
    """
    return f"dict-{csv_filename}"

def create_dictionary_file(table_name, year, output_dir):
    """Créer un fichier dictionnaire des variables pour une table donnée"""
    try:
        # Lire les variables du fichier CSV
        csv_filename = get_csv_filename(table_name, year)
        if csv_filename is None:
            print(f"❌ Aucun fichier trouvé pour la table {table_name} année {year}")
            return False
            
        csv_path = os.path.join(year, csv_filename)
        
        variables = read_csv_header(csv_path)
        if not variables:
            print(f"Impossible de lire les variables de {csv_path}")
            return False
        
        # Récupérer les définitions
        definitions = get_variable_definitions()
        table_definitions = definitions.get(table_name, {})
        
        # Créer le fichier dictionnaire dans le même dossier que le fichier source
        dict_filename = get_dict_filename(csv_filename)
        dict_path = os.path.join(year, dict_filename)
        
        with open(dict_path, 'w', encoding='utf-8') as file:
            # En-tête avec les deux colonnes de correspondances
            file.write('libelle_variable;description_variable;correspondance_codes_detaillees;correspondance_codes_simplifiees\n')
            
            # Variables
            for var in variables:
                var = var.strip()  # Nettoyer la variable
                if var in table_definitions:
                    description, correspondances = table_definitions[var]
                    # Formater automatiquement les correspondances détaillées avec guillemets si nécessaire
                    correspondances_detaillees = format_correspondances(correspondances)
                    # Créer les correspondances simplifiées
                    correspondances_simplifiees = creer_correspondances_simplifiees(var, correspondances_detaillees)
                    file.write(f'{var};{description};{correspondances_detaillees};{correspondances_simplifiees}\n')
                else:
                    print(f"Attention: Variable '{var}' non définie pour la table '{table_name}'")
                    file.write(f'{var};Description non disponible;Correspondances non disponibles;Correspondances non disponibles\n')
        
        print(f"✅ Dictionnaire créé: {dict_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du dictionnaire {table_name}: {e}")
        return False

def generate_missing_variables_report(vars_by_year):
    """
    Génère un rapport détaillé des variables exceptionnelles par année.
    """
    report_filename = "rapport_variables_exceptionnelles.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("RAPPORT DES VARIABLES EXCEPTIONNELLES PAR ANNÉE\n")
        f.write("==========================================\n\n")
        
        # Pour chaque année
        for year in sorted(vars_by_year.keys()):
            f.write(f"Année {year}\n")
            f.write("-" * 20 + "\n\n")
            
            # Pour chaque table
            for table, vars in sorted(vars_by_year[year].items()):
                if vars:  # Si il y a des variables exceptionnelles
                    f.write(f"\nTable '{table}':\n")
                    for var in sorted(vars):
                        f.write(f"  + {var}\n")
            
            f.write("\n")
        
        # Statistiques globales
        f.write("\nSTATISTIQUES GLOBALES\n")
        f.write("===================\n\n")
        
        # Compter les occurrences de chaque variable exceptionnelle
        all_exceptional_vars = {}
        for year_data in vars_by_year.values():
            for table, vars in year_data.items():
                for var in vars:
                    key = f"{table}.{var}"
                    all_exceptional_vars[key] = all_exceptional_vars.get(key, 0) + 1
        
        # Afficher les variables exceptionnelles et leur fréquence
        f.write("Variables exceptionnelles et leur fréquence d'apparition:\n")
        for var, count in sorted(all_exceptional_vars.items(), key=lambda x: (-x[1], x[0])):
            f.write(f"  + {var}: présente dans {count} année(s)\n")
    
    print(f"\n📊 Rapport des variables exceptionnelles généré: {report_filename}")

def create_all_dictionaries(start_year=2005, end_year=2023):
    """Créer tous les dictionnaires des variables pour une plage d'années donnée"""
    print(f"🚀 SCRIPT INTELLIGENT - Création des dictionnaires des variables pour les années {start_year} à {end_year}")
    print("=" * 70)
    
    tables = ['caract', 'lieux', 'vehicules', 'usagers']
    total_success = 0
    total_attempts = len(tables) * (end_year - start_year + 1)
    
    # Dictionnaire pour stocker les variables exceptionnelles par année
    exceptional_vars_by_year = {}
    
    for year in range(start_year, end_year + 1):
        year_str = str(year)
        print(f"\n📅 Traitement de l'année: {year_str}")
        
        # Initialiser le dictionnaire pour cette année
        exceptional_vars_by_year[year_str] = {}
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(year_str, exist_ok=True)
        
        success_count = 0
        for table in tables:
            print(f"\n📋 Traitement de la table: {table}")
            
            # Initialiser la liste des variables exceptionnelles pour cette table
            exceptional_vars_by_year[year_str][table] = set()
            
            # Lire les variables du fichier
            csv_filename = get_csv_filename(table, year_str)
            if csv_filename:
                variables = read_csv_header(os.path.join(year_str, csv_filename))
                if variables:
                    # Vérifier les variables exceptionnelles
                    definitions = get_variable_definitions()
                    table_definitions = definitions.get(table, {})
                    for var in variables:
                        var = var.strip()
                        if var not in table_definitions:
                            exceptional_vars_by_year[year_str][table].add(var)
                            print(f"Info: Variable exceptionnelle '{var}' trouvée dans la table '{table}'")
            
            if create_dictionary_file(table, year_str, year_str):
                success_count += 1
                total_success += 1
        
        print(f"\n✨ Résumé année {year_str}: {success_count}/{len(tables)} dictionnaires créés")
    
    print("\n" + "=" * 70)
    print(f"📊 Bilan global: {total_success}/{total_attempts} dictionnaires créés avec succès")
    
    if total_success == total_attempts:
        print("🎉 Tous les dictionnaires ont été générés avec succès!")
        print("📝 Format: correspondances détaillées ET simplifiées")
        print("🔍 Variables simplifiées: catv, manv, obs, secu1/2/3")
        print("📊 Compatible Excel avec séparateur point-virgule")
    else:
        print("⚠️  Certains dictionnaires n'ont pas pu être créés")
    
    # Générer le rapport des variables exceptionnelles
    generate_missing_variables_report(exceptional_vars_by_year)

def clean_2009_file():
    """
    Nettoie spécifiquement le fichier de caractéristiques de 2009 :
    - Remplace les tabulations par des points-virgules
    - Gère les doubles tabulations (données manquantes)
    - Préserve l'encodage et le format des caractères spéciaux
    """
    # Obtenir le chemin absolu du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "2009", "caracteristiques_2009.csv")
    temp_file = os.path.join(script_dir, "2009", "caracteristiques_2009_temp.csv")
    
    if not os.path.exists(input_file):
        print(f"❌ Fichier {input_file} non trouvé")
        return False
    
    try:
        print(f"\n🔧 Nettoyage du fichier {input_file}")
        
        # Créer une copie de sauvegarde si elle n'existe pas déjà
        backup_file = input_file + '.original'
        if not os.path.exists(backup_file):
            print(f"📑 Création d'une sauvegarde : {backup_file}")
            with open(input_file, 'rb') as f_in:
                with open(backup_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        
        # Lecture et traitement du fichier
        with open(input_file, 'r', encoding='latin1') as f_in:
            lines = f_in.readlines()
            
        # Traiter chaque ligne
        cleaned_lines = []
        for line in lines:
            # Supprimer les espaces en fin de ligne
            line = line.rstrip()
            
            # Remplacer les multiples espaces par un seul espace
            line = re.sub(r' +', ' ', line)
            
            # Remplacer les tabulations multiples par une seule tabulation
            line = re.sub(r'\t+', '\t', line)
            
            # Remplacer les tabulations par des points-virgules
            line = line.replace('\t', ';')
            
            # Ajouter la ligne nettoyée
            cleaned_lines.append(line + '\n')
        
        # Écrire le fichier nettoyé
        with open(temp_file, 'w', encoding='latin1', newline='') as f_out:
            f_out.writelines(cleaned_lines)
        
        # Remplacer le fichier original par la version nettoyée
        os.replace(temp_file, input_file)
        
        print("✅ Nettoyage terminé avec succès")
        
        # Afficher les premières lignes pour vérification
        print("\n📊 Aperçu des 3 premières lignes après nettoyage :")
        for line in cleaned_lines[:3]:
            print(line.strip())
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage : {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

if __name__ == "__main__":
    print("🤖 SCRIPT INTELLIGENT POUR DICTIONNAIRES D'ACCIDENTS CORPORELS")
    print("🔧 Fonctionnalités : ")
    print("   - Gestion automatique des guillemets pour correspondances multiples")
    print("   - Détection intelligente des formats CSV")
    print("   - Compatible Excel avec séparateur ';'")
    print("   - Extensible à toutes les années (2005-2023)")
    print("   - Correspondances détaillées ET simplifiées pour l'analyse")
    print("   - Regroupements intelligents pour catv, manv, obs, secu1/2/3")
    print("   - Nettoyage spécifique du fichier 2009 (tabulations -> points-virgules)")
    print()
    
    # Nettoyer d'abord le fichier 2009 si nécessaire
    clean_2009_file()
    
    # Puis créer les dictionnaires
    create_all_dictionaries(2005, 2023) 