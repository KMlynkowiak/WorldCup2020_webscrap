import requests
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# Twój klucz API
api_key = 'e638c28875b9437383fdf00768c5fb51'  # Wstaw swój klucz API

# Adres URL API dla wyników meczów (zwykle dla konkretnej ligi/tournamentu)
competition_id = '2000'  # ID Mistrzostw Świata 2022, zmień na odpowiednią ligę
url = f'https://api.football-data.org/v4/competitions/{competition_id}/matches'

# Nagłówki z kluczem API
headers = {
    'X-Auth-Token': api_key
}

# Wysyłanie zapytania GET
response = requests.get(url, headers=headers)

# Sprawdzenie statusu odpowiedzi
if response.status_code == 200:
    data = response.json()  # Zapisujemy odpowiedź w formacie JSON
    print("Dane o meczach pobrane pomyślnie")

    # Wyciąganie interesujących danych o meczach
    matches = data['matches']  # Lista meczów
    matches_data = []
    
    # Dodanie nazwy turnieju oraz ID turnieju
    competition_name = data['competition']['name']
    competition_id = data['competition']['id']

    for match in matches:
        try:
            home_score = match['score']['fullTime'].get('homeTeam', 'Mecz jeszcze się nie odbył')
            away_score = match['score']['fullTime'].get('awayTeam', 'Mecz jeszcze się nie odbył')
        except KeyError:
            home_score, away_score = 'Mecz jeszcze się nie odbył', 'Mecz jeszcze się nie odbył'

        # Przekształcenie daty na format YYYY MM DD
        iso_date = match['utcDate']
        date_obj = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))  # Zamiana 'Z' na '+00:00' aby było poprawnie parsowane
        formatted_date = date_obj.strftime("%Y %m %d")

        # Wyciągnięcie zwycięzcy
        winner = match['score']['winner']
        if winner == 'HOME_TEAM':
            winner_team = match['homeTeam']['name']
        elif winner == 'AWAY_TEAM':
            winner_team = match['awayTeam']['name']
        else:
            winner_team = 'Remis'

        matches_data.append({
            'competition_id': competition_id,  # Dodanie ID turnieju
            'competition_name': competition_name,  # Dodanie nazwy turnieju
            'home_team': match['homeTeam']['name'],
            'away_team': match['awayTeam']['name'],
            'date': formatted_date,  # Zmieniona data na format YYYY MM DD
            'winner': winner_team  # Zwycięzca spotkania
        })

    # Tworzenie DataFrame
    df = pd.DataFrame(matches_data)

    # Wyświetlanie danych
    print(df)

    # Zapis danych do SQLite
    conn = sqlite3.connect('football_data.db')
    df.to_sql('matches', conn, if_exists='replace', index=False)
    conn.close()

    print("Dane o meczach zapisane do bazy SQLite.")

    # Policzmy, ile razy każdy kraj wygrał
    winner_counts = df['winner'].value_counts()

    # Wyświetlenie danych
    print(winner_counts)

    # Tworzymy wykres
    plt.figure(figsize=(10,6))
    winner_counts.plot(kind='bar', color='skyblue')

    # Dodanie tytułu i etykiet
    plt.title('Liczba wygranych meczy przez drużyny')
    plt.xlabel('Drużyna')
    plt.ylabel('Liczba wygranych meczy')

    # Wyświetlenie wykresu
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

else:
    print(f"Błąd pobierania danych o meczach. Kod odpowiedzi: {response.status_code}")
