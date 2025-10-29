import requests
from bs4 import BeautifulSoup
import pandas as pd


URL_BASE = 'http://books.toscrape.com/index.html'
URL_SITIO = 'http://books.toscrape.com/'

datos_libros = []


def obtener_estrellas(etiqueta_articulo):

    rating_clase = etiqueta_articulo.find('p', class_='star-rating')['class']

    rating_texto = rating_clase[1]

    if rating_texto == 'One':
        return 1
    elif rating_texto == 'Two':
        return 2
    elif rating_texto == 'Three':
        return 3
    elif rating_texto == 'Four':
        return 4
    elif rating_texto == 'Five':
        return 5
    return 0


def realizar_scraping_pagina(url_pagina):
    print(f"Haciendo scraping de: {url_pagina}")

    try:
        response = requests.get(url_pagina)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la URL {url_pagina}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    articulos_libros = soup.find_all('article', class_='product_pod')

    for articulo in articulos_libros:
        titulo = articulo.h3.a['title']

        precio_texto = articulo.find('p', class_='price_color').text
        precio = float(precio_texto.replace('£', ''))

        rating = obtener_estrellas(articulo)

        imagen_relativa = articulo.find('img', class_='thumbnail')['src']
        enlace_portada = URL_SITIO + imagen_relativa.replace('../..', '')

        stock_texto = articulo.find('p', class_='instock availability').text.strip()

        datos_libros.append({
            'Titulo': titulo,
            'Precio_GBP': precio,
            'Rating_Estrellas': rating,
            'Disponibilidad': stock_texto,
            'Enlace_Portada': enlace_portada
        })

    siguiente_enlace = soup.find('li', class_='next')
    if siguiente_enlace and siguiente_enlace.a:
        ruta_siguiente = siguiente_enlace.a['href']

        url_base_actual = url_pagina.rsplit('/', 1)[0] + '/'

        if 'index.html' in url_pagina:
            return URL_SITIO + ruta_siguiente
        else:
            return url_base_actual + ruta_siguiente

    return None


url_actual = URL_BASE
contador_paginas = 0

while url_actual:
    url_actual = realizar_scraping_pagina(url_actual)
    contador_paginas += 1

print(f"\nScraping completado. Total de páginas procesadas: {contador_paginas}")
print(f"Total de libros extraídos: {len(datos_libros)}")

if datos_libros:
    df = pd.DataFrame(datos_libros)

    NOMBRE_ARCHIVO_CSV = 'datos_libros_scraping.csv'
    df.to_csv(NOMBRE_ARCHIVO_CSV, index=False, encoding='utf-8')

    print(f"\nDatos guardados exitosamente en: {NOMBRE_ARCHIVO_CSV}")
    print("\nPrimeras 5 filas del DataFrame:")
    print(df.head())
else:
    print("No se extrajeron datos para guardar.")