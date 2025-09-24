import requests
import pandas as pd
from datetime import datetime
import time
import calendar

# Configuration
STATION = "FKKD"  # Aéroport de Douala
YEARS = [2022, 2023, 2024]
OUTPUT_FILE = f"donnees_meteo_{STATION}_{YEARS[0]}-{YEARS[-1]}.csv"
BASE_URL = "https://www.ogimet.com/display_metars2.php"

def get_last_day(year, month):
    return calendar.monthrange(year, month)[1]

def fetch_ogimet_data(year, month):
    last_day = get_last_day(year, month)
    
    params = {
        'lang': 'fr',
        'lugar': STATION,
        'tipo': 'ALL',
        'ord': 'REV',
        'nil': 'SI',
        'fmt': 'txt',
        'ano': year,
        'mes': month,
        'day': 1,
        'hora': 0,
        'anof': year,
        'mesf': month,
        'dayf': last_day,
        'horaf': 23,
        'send': 'send'
    }

    print(f"Récupération {STATION} - {year}-{month:02d}...")
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=60)
        response.raise_for_status()
        
        # Debug: Sauvegarder la réponse brute pour inspection
        with open(f"debug_{year}_{month}.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        return response.text
    except Exception as e:
        print(f"Erreur pour {year}-{month:02d}: {str(e)}")
        return None

def parse_metar_data(raw_data):
    if not raw_data:
        return None
        
    lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
    data = []
    
    for line in lines:
        if not line.startswith(STATION):
            continue
            
        try:
            # Format: FKKD 202201010000 AUTO 27010KT 9999 TSRA SCT025CB 27/23 Q1010
            parts = line.split()
            if len(parts) < 6:
                continue
                
            # Extraction date/heure
            date_str = parts[1] + parts[2]
            date_time = datetime.strptime(date_str, "%Y%m%d%H%M")
            
            # Initialisation des variables
            metar = {
                'date': date_time,
                'temperature': None,
                'point_de_rosee': None,
                'pression': None,
                'direction_vent': None,
                'vitesse_vent': None
            }
            
            # Analyse des éléments METAR
            for item in parts[3:]:
                if '/' in item and len(item.split('/')[0]) == 2:
                    temp, dew = item.split('/')
                    metar['temperature'] = float(temp) if temp != 'MM' else None
                    metar['point_de_rosee'] = float(dew) if dew != 'MM' else None
                elif item.startswith('Q'):
                    metar['pression'] = float(item[1:]) if item[1:] != 'MM' else None
                elif 'KT' in item:
                    wind_part = item.replace('KT', '')
                    if len(wind_part) >= 3:
                        metar['direction_vent'] = float(wind_part[:3])
                        if len(wind_part) > 3:
                            metar['vitesse_vent'] = float(wind_part[3:])
            
            data.append(metar)
        except Exception as e:
            print(f"Erreur parsing ligne: {line}\n{str(e)}")
            continue
            
    return pd.DataFrame(data) if data else None

def main():
    all_data = []
    
    for year in YEARS:
        for month in range(1, 13):
            raw_data = fetch_ogimet_data(year, month)
            if raw_data:
                df = parse_metar_data(raw_data)
                if df is not None and not df.empty:
                    all_data.append(df)
                    print(f"Données trouvées: {len(df)} enregistrements")
                else:
                    print("Aucune donnée valide dans la réponse")
            time.sleep(3)  # Respect du serveur
            
    if not all_data:
        print("Aucune donnée valide récupérée. Vérifiez les fichiers debug_*.txt")
        return
        
    final_df = pd.concat(all_data).sort_values('date').reset_index(drop=True)
    
    # Sauvegarde
    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n✅ Données sauvegardées dans {OUTPUT_FILE}")
    print(f"Période couverte: {final_df['date'].min()} - {final_df['date'].max()}")
    print(f"Nombre d'observations: {len(final_df)}")

if __name__ == "__main__":
    main()