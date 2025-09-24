import requests
import pandas as pd
from datetime import datetime
import time
import calendar
import re

# Configuration
STATION = "FKKD"  # Aéroport de Douala
YEARS = [2022]
MONTHS = range(1, 13)  # Tous les mois
OUTPUT_FILE = f"donnees_meteo_{STATION}_2022.csv"
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
        'nil': 'NO',
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
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Erreur pour {year}-{month:02d}: {str(e)}")
        return None

def parse_metar_data(raw_data):
    if not raw_data:
        return None
        
    # Expression régulière pour extraire les METAR
    metar_pattern = re.compile(
        r'(\d{12}) METAR (\w{4}) (\d{6}Z) (\w{3}\d{2}KT).*?(\d{2})/(\d{2}) Q(\d{4})',
        re.DOTALL
    )
    
    data = []
    
    for match in metar_pattern.finditer(raw_data):
        try:
            date_str = match.group(1)  # YYYYMMDDHHmm
            station = match.group(2)
            time_str = match.group(3)  # DDHHmmZ
            wind = match.group(4)
            temp = match.group(5)
            dew_point = match.group(6)
            pressure = match.group(7)
            
            # Convertir la date
            date_time = datetime.strptime(date_str[:8], "%Y%m%d")
            hour_min = date_str[8:12]
            
            # Extraire la direction et vitesse du vent
            wind_dir = wind[:3] if wind[:3].isdigit() else None
            wind_speed = wind[3:5] if wind[3:5].isdigit() else None
            
            data.append({
                'date': date_time,
                'heure': hour_min[:2] + ':' + hour_min[2:],
                'station': station,
                'temperature': float(temp),
                'point_de_rosee': float(dew_point),
                'pression': float(pressure)/10,  # Convertir hPa en kPa
                'direction_vent': wind_dir,
                'vitesse_vent': wind_speed
            })
        except Exception as e:
            print(f"Erreur parsing METAR: {str(e)}")
            continue
            
    return pd.DataFrame(data) if data else None

def main():
    all_data = []
    
    for year in YEARS:
        for month in MONTHS:
            raw_data = fetch_ogimet_data(year, month)
            if raw_data:
                # Sauvegarder les données brutes pour débogage
                with open(f"raw_{year}_{month:02d}.txt", "w", encoding="utf-8") as f:
                    f.write(raw_data)
                
                df = parse_metar_data(raw_data)
                if df is not None and not df.empty:
                    all_data.append(df)
                    print(f"Données trouvées: {len(df)} enregistrements")
                else:
                    print("Aucune donnée valide dans la réponse")
            time.sleep(2)  # Respect du serveur
            
    if not all_data:
        print("Aucune donnée valide récupérée. Vérifiez les fichiers raw_*.txt")
        return
        
    final_df = pd.concat(all_data).sort_values(['date', 'heure']).reset_index(drop=True)
    
    # Sauvegarde
    final_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"\n✅ Données sauvegardées dans {OUTPUT_FILE}")
    print(f"Période couverte: {final_df['date'].min().date()} - {final_df['date'].max().date()}")
    print(f"Nombre d'observations: {len(final_df)}")

if __name__ == "__main__":
    main()