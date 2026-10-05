import os
import sys
import json
import time
import urllib.request
import urllib.parse

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'PointNemoDocumentary/1.0 (Windows NT 10.0; Win64; x64; edu-channel)'
}

def download_file(url, target_path):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=40) as resp, open(target_path, 'wb') as f:
        f.write(resp.read())

def search_wikimedia(query, filename, is_video=False):
    target = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(target) and os.path.getsize(target) > 20000:
        print(f"[YA EXISTE] {filename}")
        return True

    prefix = "filetype:video " if is_video else ""
    full_query = prefix + query
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
        f"&generator=search&gsrsearch={urllib.parse.quote(full_query)}"
        f"&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url|mime|size"
    )
    time.sleep(1.2)
    req = urllib.request.Request(api_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, page in pages.items():
                infos = page.get('imageinfo', [])
                if infos:
                    url = infos[0].get('url')
                    # Prefer high resolution
                    print(f"Descargando de Wikimedia: {filename}...")
                    time.sleep(1.0)
                    download_file(url, target)
                    print(f"   [OK] Guardado: {filename} ({os.path.getsize(target)//1024} KB)")
                    return True
        print(f"No se encontró en Wikimedia: {query}")
        return False
    except Exception as e:
        print(f"Error descargando {filename} de Wikimedia: {e}")
        return False

def search_nasa_image(query, filename):
    target = os.path.join(MEDIA_DIR, filename)
    if os.path.exists(target) and os.path.getsize(target) > 20000:
        print(f"[YA EXISTE] {filename}")
        return True

    api_url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type=image"
    time.sleep(1.0)
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('collection', {}).get('items', [])
            if items:
                href = items[0].get('href') # json of image variants
                with urllib.request.urlopen(urllib.request.Request(href, headers={'User-Agent': 'Mozilla/5.0'})) as iresp:
                    img_urls = json.loads(iresp.read().decode('utf-8'))
                    # find medium or large
                    selected = None
                    for u in img_urls:
                        if '~large.jpg' in u or '~medium.jpg' in u or '.jpg' in u:
                            selected = u
                            break
                    if selected:
                        print(f"Descargando de NASA: {filename}...")
                        download_file(selected, target)
                        print(f"   [OK] Guardado: {filename} ({os.path.getsize(target)//1024} KB)")
                        return True
        return False
    except Exception as e:
        print(f"Error descargando de NASA {filename}: {e}")
        return False

# Plan de medios para los 6 actos de Punto Nemo
MEDIA_PLAN = [
    # Acto 1: Introducción y Coordenadas del Aislamiento
    {"source": "wiki", "query": "Location of Point Nemo in the South Pacific Ocean", "file": "01_mapa_punto_nemo_localizacion.png"},
    {"source": "wiki", "query": "Oceanic pole of inaccessibility", "file": "02_mapa_polo_inaccesibilidad.png"},
    {"source": "wiki", "query": "Pacific Ocean horizon dark waves", "file": "03_oceano_vasto_solitario.jpg"},
    {"source": "nasa", "query": "Earth from International Space Station Pacific", "file": "04_tierra_desde_iss_pacifico.jpg"},
    {"source": "nasa", "query": "Astronaut in Cupola looking at Earth", "file": "05_astronauta_cupola_observando.jpg"},

    # Acto 2: El Cementerio de Naves Espaciales
    {"source": "nasa", "query": "Mir space station orbit", "file": "06_estacion_espacial_mir.jpg"},
    {"source": "wiki", "query": "Mir deorbit atmospheric entry fire", "file": "07_reingreso_atmosferico_fuego.jpg"},
    {"source": "nasa", "query": "Progress spacecraft uncrewed cargo", "file": "08_nave_cargo_progress.jpg"},
    {"source": "wiki", "query": "Spacecraft cemetery underwater wreck", "file": "09_restos_espaciales_submarinos.jpg"},

    # Acto 3: El Sonido "The Bloop"
    {"source": "wiki", "query": "Bloop spectrogram NOAA", "file": "10_bloop_espectrograma_noaa.png"},
    {"source": "wiki", "query": "NOAA Autonomous Hydrophone underwater", "file": "11_hidrofono_submarino_noaa.jpg"},
    {"source": "wiki", "query": "Deep ocean trench abyssal darkness", "file": "12_abismo_marino_profundo.jpg"},
    {"source": "wiki", "query": "Antarctic iceberg calving cryoseism", "file": "13_iceberg_criosismo_antartida.jpg"},

    # Acto 4: El Desierto Biológico Marino
    {"source": "wiki", "query": "South Pacific Gyre ocean currents", "file": "14_giro_pacifico_sur_corrientes.png"},
    {"source": "wiki", "query": "Clear blue oligotrophic ocean water", "file": "15_aguas_azules_desierto_marino.jpg"},
    {"source": "wiki", "query": "Marine plankton microscopy empty", "file": "16_fitoplancton_ausencia_vida.jpg"},

    # Acto 5: Lovecraft y la Ciudad de R'lyeh
    {"source": "wiki", "query": "Call of Cthulhu Lovecraft map Rlyeh", "file": "17_lovecraft_rlyeh_mapa.jpg"},
    {"source": "wiki", "query": "Underwater sunken monolith ruins", "file": "18_ruinas_sumergidas_abismo.jpg"},
    {"source": "wiki", "query": "Mythology sea monster kraken ancient", "file": "19_monstruo_marino_profundidades.jpg"},

    # Acto 6: El Destino 2031 de la ISS y Cierre
    {"source": "nasa", "query": "International Space Station full view high res", "file": "20_estacion_espacial_internacional_hd.jpg"},
    {"source": "nasa", "query": "Spacecraft burning atmospheric reentry simulation", "file": "21_caida_iss_bola_de_fuego.jpg"},
    {"source": "wiki", "query": "Vast empty Pacific Ocean twilight sunset", "file": "22_atardecer_crepusculo_oceano.jpg"}
]

def main():
    print(f"=== Descargando {len(MEDIA_PLAN)} recursos visuales para el documental Punto Nemo ===")
    success = 0
    for item in MEDIA_PLAN:
        if item["source"] == "wiki":
            ok = search_wikimedia(item["query"], item["file"])
        elif item["source"] == "nasa":
            ok = search_nasa_image(item["query"], item["file"])
        else:
            ok = False
            
        # Fallback if primary fails
        if not ok:
            print(f"Intentando fallback para {item['file']}...")
            ok = search_wikimedia(item["query"].split()[0] + " ocean", item["file"])
        if ok:
            success += 1
            
    print(f"\nFinalizado: {success}/{len(MEDIA_PLAN)} archivos listos en media/")

if __name__ == "__main__":
    main()
