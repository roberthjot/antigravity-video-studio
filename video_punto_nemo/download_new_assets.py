import os
import requests
import urllib.parse
from PIL import Image

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")

HEADERS = {'User-Agent': 'PointNemoDoc8Min/1.0 (Windows NT 10.0; Win64; x64)'}

ITEMS = [
    ("Volvo Ocean Race storm waves", "22_ocean_race_sailboat_storm.jpg"),
    ("Sailing ship storm southern ocean", "23_velero_olas_gigantes.jpg"),
    ("NASA spacewalk Earth background", "24_spacewalk_astronauta.jpg"),
    ("Ship radar screen ocean navigation", "25_pantalla_radar_navegacion.jpg"),
    ("Underwater abyss sea floor deep", "26_lecho_marino_abismo.jpg")
]

for q, fn in ITEMS:
    target = os.path.join(MEDIA_DIR, fn)
    if os.path.exists(target) and os.path.getsize(target) > 20000:
        continue
    url_api = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(q)}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url"
    try:
        r = requests.get(url_api, headers=HEADERS, timeout=10)
        pages = r.json().get('query', {}).get('pages', {})
        for pid, page in pages.items():
            infos = page.get('imageinfo', [])
            if infos:
                img_url = infos[0].get('url')
                print(f"Descargando {fn}...")
                ir = requests.get(img_url, headers=HEADERS, timeout=15)
                if len(ir.content) > 10000:
                    with open(target, 'wb') as f:
                        f.write(ir.content)
                    try:
                        with Image.open(target) as im:
                            im.verify()
                        print(f"   [OK VALID] {fn} ({os.path.getsize(target)//1024} KB)")
                        break
                    except Exception as e:
                        if os.path.exists(target): os.remove(target)
    except Exception as e:
        print(f"Error {q}: {e}")
