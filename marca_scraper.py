from bs4 import BeautifulSoup
import requests
import sqlite3
import re

urls = [
    "https://www.marca.com/futbol.html?intcmp=MENUPROD&s_kw=futbol",
    "https://www.marca.com/futbol/real-madrid/2025/09/24/madrid-llega-lanzado-derbi.html",
    "https://www.marca.com/futbol/primera-division/2025/09/24/atletico-rayo-vallecano-derbi-crucial-gran-derbi.html",
    "https://www.marca.com/futbol/primera-division/2025/09/23/getafe-alaves-mirar-abajo-previa-analisis-pronostico-prediccion.html",
    "https://www.marca.com/futbol/primera-division/2025/09/24/real-sociedad-mallorca-victoria-esperar-previa-analisis-pronostico-prediccion.html",
    "https://www.marca.com/futbol/europa-league/2025/09/24/betis-nottingham-forest-abran-paso-vuelve-eurobetis.html"
]

conn = sqlite3.connect('noticias.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,
    enlace TEXT,
    fecha TEXT,
    autor TEXT
)
''')
cursor.execute('DELETE FROM noticias')  
conn.commit()

noticias = []
noticias_guardadas = 0

for url in urls:
    response = requests.get(url)
    if response.status_code != 200:
        continue
    soup = BeautifulSoup(response.text, "html.parser")


    if "futbol.html" in url:
        titulos = soup.find_all(class_="ue-c-cover-content__headline")
        for t in titulos:
            if noticias_guardadas >= 10:
                break
            titulo = t.get_text(strip=True)[:150]
            enlace_tag = t.find_parent('a')
            enlace = enlace_tag['href'] if enlace_tag else url

            
            fecha_match = re.search(r'/(\d{4}/\d{2}/\d{2})/', enlace)
            if fecha_match:
                partes = fecha_match.group(1).split('/')
                fecha = f"{partes[2]}/{partes[1]}/{partes[0]}"
            else:
                fecha = "Desconocida"

            autor = "Marca"

            noticias.append((titulo, enlace, fecha, autor))
            noticias_guardadas += 1

 
    else:
        header = soup.find("div", class_="ue-l-article__header")
        header_texto = header.get_text(strip=True, separator=" ") if header else "Sin título"

        fecha_match = re.search(r'/(\d{4}/\d{2}/\d{2})/', url)
        if fecha_match:
            partes = fecha_match.group(1).split('/')
            fecha = f"{partes[2]}/{partes[1]}/{partes[0]}"
        else:
            fecha = "Desconocida"

        autor = "Marca"

        if noticias_guardadas < 10:
            noticias.append((header_texto[:150], url, fecha, autor))
            noticias_guardadas += 1

cursor.executemany('''
INSERT INTO noticias (titulo, enlace, fecha, autor)
VALUES (?, ?, ?, ?)
''', noticias)
conn.commit()
conn.close()

print(f"{len(noticias)} noticias guardadas en SQLite.")
