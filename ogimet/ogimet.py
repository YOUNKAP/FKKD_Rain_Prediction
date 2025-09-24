import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from io import StringIO
import calendar

# Paramètres de configuration
STATION = "FKKD"  # Code de la station météo de Douala
ANNEES = [2022, 2023, 2024]
URL_BASE = "https://www.ogimet.com/cgi-bin/gsynres"
DELAI = 2  # Délai en secondes entre les requêtes
FICHIER_SORTIE = f"donnees_meteo_{STATION}_2022_2024.xlsx"

def obtenir_dernier_jour_mois(annee, mois):
    """Retourne le dernier jour du mois donné"""
    return calendar.monthrange(annee, mois)[1]

def normaliser_noms_colonnes(colonnes):
    """Normalise les noms de colonnes"""
    noms_normalises = []
    for col in colonnes:
        if isinstance(col, str):
            noms_normalises.append(col.strip().lower())
        else:
            noms_normalises.append(str(col).lower())
    return noms_normalises

def recuperer_donnees_mensuelles(annee, mois):
    """
    Récupère les données météo pour un mois et une année spécifiques
    Retourne un DataFrame ou None en cas d'échec
    """
    dernier_jour = obtenir_dernier_jour_mois(annee, mois)
    
    parametres = {
        "lang": "en",
        "ind": STATION,
        "ndays": str(dernier_jour),
        "ano": str(annee),
        "mes": str(mois),
        "day": "01",
        "hora": "00",
        "ord": "DIR",
        "send": "send"
    }

    print(f"Téléchargement : {STATION} - {annee}-{mois:02d}...")

    try:
        reponse = requests.get(URL_BASE, params=parametres, timeout=30)
        reponse.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur de téléchargement {annee}-{mois:02d}: {e}")
        return None

    soup = BeautifulSoup(reponse.text, "html.parser")
    tableau = soup.find("table")

    if not tableau:
        print(f"Aucune donnée trouvée pour {STATION} - {annee}-{mois:02d}")
        return None

    try:
        # Lire le tableau HTML
        dfs = pd.read_html(StringIO(str(tableau)))
        if not dfs:
            print(f"Aucun tableau trouvé dans la réponse pour {annee}-{mois:02d}")
            return None
            
        df = dfs[0]
        
        # Normaliser les noms de colonnes
        df.columns = normaliser_noms_colonnes(df.columns)
        
        # Ajouter les colonnes année et mois
        df["annee"] = annee
        df["mois"] = mois
        
        return df
    except Exception as e:
        print(f"Erreur d'analyse des données pour {annee}-{mois:02d}: {str(e)}")
        return None

def main():
    """Fonction principale qui orchestre le téléchargement"""
    toutes_donnees = []

    for annee in ANNEES:
        for mois in range(1, 13):
            donnees_mois = recuperer_donnees_mensuelles(annee, mois)
            if donnees_mois is not None:
                toutes_donnees.append(donnees_mois)
            sleep(DELAI)

    if not toutes_donnees:
        print("Aucune donnée n'a pu être récupérée.")
        return

    # Fusionner toutes les données
    resultat = pd.concat(toutes_donnees, ignore_index=True)
    
    # Afficher les colonnes disponibles pour le débogage
    print("\nColonnes disponibles dans les données:")
    print(resultat.columns.tolist())
    
    # Sauvegarde en Excel
    resultat.to_excel(FICHIER_SORTIE, index=False)
    print(f"\n✅ Données sauvegardées avec succès dans {FICHIER_SORTIE}")

    # Statistiques de base
    print(f"\nNombre total d'enregistrements : {len(resultat)}")
    
    # Vérification de la présence de colonnes temporelles
    colonnes_temporelles = ['date', 'time', 'datetime']
    for col in colonnes_temporelles:
        if col in resultat.columns:
            print(f"Plage temporelle ({col}): {resultat[col].min()} à {resultat[col].max()}")
            break
    else:
        print("Aucune colonne temporelle trouvée (date/time/datetime)")

if __name__ == "__main__":
    main()