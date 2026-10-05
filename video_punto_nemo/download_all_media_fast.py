import os
import sys
import requests
import json
import time

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    'User-Agent': 'DocumentaryNemoProducer/1.0 (Windows NT 10.0; Win64; x64; edu-project)'
})

def download_file(url, target_path):
    url = url.replace('http://', 'https://')
    try:
        r = session.get(url, timeout=12)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            return True
        return False
    except Exception as e:
        print(f"   [Error {url[:50]}...]: {e}")
        return False

def fetch_wiki(query, filename):
    target = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(target) and os.path.getsize(target) > 20000:
        print(f"[YA EXISTE] {filename}")
        return True

    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
        f"&generator=search&gsrsearch={query}"
        f"&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url|mime|size"
    )
    try:
        r = session.get(api_url, timeout=8)
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for pid, page in pages.items():
            infos = page.get('imageinfo', [])
            if infos:
                url = infos[0].get('url')
                print(f"Descargando {filename} desde Wikimedia...")
                if download_file(url, target):
                    print(f"   [OK] {filename} ({os.path.getsize(target)//1024} KB)")
                    return True
    except Exception as e:
        print(f"Error Wiki {query}: {e}")
    return False

def fetch_nasa(query, filename):
    target = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(target) and os.path.getsize(target) > 20000:
        print(f"[YA EXISTE] {filename}")
        return True

    api_url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"
    try:
        r = session.get(api_url, timeout=8)
        items = r.json().get('collection', {}).get('items', [])
        if items:
            href = items[0].get('href').replace('http://', 'https://')
            r2 = session.get(href, timeout=8)
            img_urls = r2.json()
            selected = None
            for u in img_urls:
                if '~large.jpg' in u or '~medium.jpg' in u or u.endswith('.jpg'):
                    selected = u
                    break
            if selected:
                print(f"Descargando {filename} desde NASA...")
                if download_file(selected, target):
                    print(f"   [OK] {filename} ({os.path.getsize(target)//1024} KB)")
                    return True
    except Exception as e:
        print(f"Error NASA {query}: {e}")
    return False

ASSETS = [
    # Acto 1: Introducción y Ubicación
    ("wiki", "Point Nemo Pacific Ocean", "01_mapa_punto_nemo_localizacion.png"),
    ("wiki", "Oceanic pole of inaccessibility", "02_mapa_polo_inaccesibilidad.png"),
    ("nasa", "Earth South Pacific ISS", "03_tierra_pacifico_desde_iss.jpg"),
    ("nasa", "Astronaut in Cupola viewing Earth", "04_astronauta_cupola.jpg"),

    # Acto 2: El Cementerio Espacial
    ("nasa", "Mir space station", "05_estacion_espacial_mir.jpg"),
    ("nasa", "Progress spacecraft", "06_carguero_progress.jpg"),
    ("wiki", "Spacecraft atmospheric entry", "07_reingreso_atmosferico_fuego.jpg"),
    ("wiki", "Shipwreck underwater coral", "08_restos_submarinos_fondo.jpg"),

    # Acto 3: The Bloop y el Abismo
    ("wiki", "Bloop spectrogram NOAA", "09_bloop_espectrograma.png"),
    ("wiki", "Hydrophone underwater ocean", "10_hidrofono_submarino.jpg"),
    ("wiki", "Mariana Trench deep ocean", "11_abismo_oceano_profundo.jpg"),
    ("wiki", "Iceberg Antarctica calving", "12_iceberg_antartida_criosismo.jpg"),

    # Acto 4: El Desierto Biológico Marino
    ("wiki", "South Pacific Gyre ocean currents", "13_giro_pacifico_sur.png"),
    ("wiki", "Pacific Ocean deep blue water", "14_aguas_azules_desierto_marino.jpg"),
    ("wiki", "Marine plankton microscope", "15_microorganismos_marinos.jpg"),

    # Acto 5: Lovecraft y R'lyeh
    ("wiki", "Cthulhu monster mythical", "16_cthulhu_monstruo_marino.jpg"),
    ("wiki", "Sunken city ruins underwater", "17_ciudad_sumergida_ruinas.jpg"),
    ("wiki", "Kraken sea monster vintage", "18_criatura_abisal_mitologia.jpg"),

    # Acto 6: Fin de la ISS 2031 y Conclusión
    ("nasa", "International Space Station 2021", "19_estacion_espacial_internacional.jpg"),
    ("nasa", "Spacecraft reentry fireball meteor", "20_reingreso_bola_de_fuego.jpg"),
    ("wiki", "Pacific Ocean sunset golden horizon", "21_atardecer_dorado_pacifico.jpg")
]

def main():
    print("Iniciando descarga rápida de recursos para Punto Nemo...\n")
    for src, q, fn in ASSETS:
        target = os.path.join(MEDIA_DIR, fn)
        if os.path.exists(target) and os.path.getsize(target) > 20000:
            print(f"[YA EXISTE] {fn}")
            continue
        if src == "wiki":
            ok = fetch_wiki(q, fn)
        else:
            ok = fetch_nasa(q, fn)
        if not ok:
            # Fallback rápido a Wiki
            fetch_wiki("ocean", fn)
        time.sleep(0.4)
    print("\nProceso de descarga terminado.")

if __name__ == "__main__":
    main()
