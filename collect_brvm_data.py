import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import os

BASE_URL = "https://www.economie-ivoirienne.ci/brvm-all?page={}#"

def extract_table_data(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    table = soup.find('table', class_='views-table')
    
    if not table:
        print("Tableau non trouvé sur cette page.")
        return None

    data_rows = []
    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        if cols:
            cleaned_row = [col.get_text(strip=True) for col in cols]
            data_rows.append(cleaned_row)

    return data_rows if data_rows else None

def get_all_data():
    all_data = []
    page_num = 0
    print("Début de la récupération des données...")

    while True:
        print(f"  - Récupération de la page {page_num}...")
        url = BASE_URL.format(page_num)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            page_data = extract_table_data(response.text)
            
            if page_data is None:
                print(f"    -> Plus de données trouvées. Arrêt.")
                break
                
            all_data.extend(page_data)
            time.sleep(1)
            page_num += 1
            
        except requests.exceptions.RequestException as e:
            print(f"    -> Erreur: {e}")
            break
        except Exception as e:
            print(f"    -> Erreur inattendue: {e}")
            break

    if not all_data:
        print("Aucune donnée récupérée.")
        return None
        
    columns = ['Date', 'Valeur_des_transactions', 'Capitalisation_Actions', 
               'Capitalisation_Obligations', 'BRVM_10', 'BRVM_Composite', 
               'Taux_BRVM_10', 'BRVM_PRESTIGE']
    
    df = pd.DataFrame(all_data, columns=columns)
    df.dropna(how='all', inplace=True)
    
    print(f"Récupération terminée. {len(df)} lignes collectées.")
    return df

def save_data(df):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    filepath = 'data/brvm_market_data.csv'
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"Données sauvegardées dans '{filepath}'")

if __name__ == "__main__":
    print("Collecte des données boursières de la BRVM")
    data_frame = get_all_data()
    if data_frame is not None:
        print("\nAperçu des données (5 premières lignes) :")
        print(data_frame.head())
        save_data(data_frame)
    else:
        print("Le script n'a pas pu collecter les données.")
