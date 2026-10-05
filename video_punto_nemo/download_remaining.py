import os
import requests
import urllib.parse

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")

HEADERS = {'User-Agent': 'PointNemoDoc/1.0 (Windows NT 10.0; Win64; x64)'}

ITEMS = [
    ("South Pacific Gyre", "13_giro_pacifico_sur.png"),
    ("Pacific Ocean water", "14_aguas_azules_desierto_marino.jpg"),
    ("Cthulhu", "16_cthulhu_monstruo_marino.jpg"),
    ("Underwater ruins", "17_ciudad_sumergida_ruinas.jpg"),
    ("Sea monster mythology", "18_criatura_abisal_mitologia.jpg"),
    ("Space shuttle reentry fireball", "20_reingreso_bola_de_fuego.jpg")
]

for q, fn in ITEMS:
    target = os.path.join(MEDIA_DIR, fn)
    if os.path.exists(target) and os.path.getsize(target) > 10000:
        continue
    url_api = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(q)}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url"
    try:
        r = requests.get(url_api, headers=HEADERS, timeout=10)
        pages = r.json().get('query', {}).get('pages', {})
        for pid, page in pages.items():
            infos = page.get('imageinfo', [])
            if infos:
                img_url = infos[0].get('url')
                print(f"Descargando {fn} desde {img_url[:60]}...")
                ir = requests.get(img_url, headers=HEADERS, timeout=15)
                if len(ir.content) > 5000:
                    with open(target, 'wb') as f:
                        f.write(ir.content)
                    print(f"   [OK] {fn} ({os.path.getsize(target)//1024} KB)")
                    break
    except Exception as e:
        print(f"Error con {q}: {e}")
