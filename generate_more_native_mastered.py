import os
import sys
import asyncio
import edge_tts
import subprocess
import imageio_ffmpeg

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_barcos_modernos"
OUT_DIR = os.path.join(PROJECT_DIR, "muestras_voces")
os.makedirs(OUT_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Frases de prueba con cadencia natural y pausas
TEXTO_DOCUMENTAL = (
    "En las profundidades del océano Atlántico... la ingeniería humana enfrenta su mayor desafío. "
    "Gigantes de acero capaces de resistir olas de más de treinta metros, navegando hacia lo desconocido. "
    "Hoy descubriremos cómo estas colosales estructuras logran desafiar a la naturaleza."
)

TEXTO_MISTERIO = (
    "Durante décadas... se creyó imposible descender a esas profundidades sin ser aplastado por la presión. "
    "Sin embargo, lo que los radares detectaron en el fondo de la fosa... cambió las reglas para siempre."
)

TEXTO_VIRAL = (
    "¿Sabías que un buque portacontenedores moderno transporta más carga que mil aviones juntos? "
    "Su motor pesa más de dos mil toneladas... ¡y consume miles de litros por hora! "
    "Mira esto hasta el final para entender cómo funciona."
)

# Filtros de masterización según el estilo
FILTER_DOCUMENTAL = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

FILTER_GRAVE_CINE = (
    "highpass=f=65,"
    "equalizer=f=140:t=q:w=1.8:g=4.5,"
    "equalizer=f=3400:t=q:w=1.2:g=2.0,"
    "acompressor=threshold=-20dB:ratio=4.0:attack=20:release=160:makeup=3.0,"
    "alimiter=limit=-1dB"
)

FILTER_DINAMICO_SHORTS = (
    "highpass=f=85,"
    "equalizer=f=220:t=q:w=1.2:g=2.5,"
    "equalizer=f=3500:t=q:w=1.0:g=3.0,"
    "acompressor=threshold=-16dB:ratio=4.0:attack=10:release=100:makeup=3.0,"
    "alimiter=limit=-1dB"
)

NUEVAS_VOCES = [
    {
        "id": "nativo_06_alonso_latino_neutro_tv",
        "voice": "es-US-AlonsoNeural",
        "rate": "+0%",
        "pitch": "-2Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_DOCUMENTAL,
        "desc": "Alonso (Latino Neutro / TV) - Estilo Documental Comercial Moderno"
    },
    {
        "id": "nativo_07_paloma_latina_neutra_elegante",
        "voice": "es-US-PalomaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_DOCUMENTAL,
        "desc": "Paloma (Latina Neutra) - Femenina Elegante y Muy Natural"
    },
    {
        "id": "nativo_08_ximena_espana_narradora",
        "voice": "es-ES-XimenaNeural",
        "rate": "-1%",
        "pitch": "-1Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_DOCUMENTAL,
        "desc": "Ximena (España) - Narración Moderna, Limpia y Cristalina"
    },
    {
        "id": "nativo_09_tomas_argentina_misterio",
        "voice": "es-AR-TomasNeural",
        "rate": "-3%",
        "pitch": "-2Hz",
        "text": TEXTO_MISTERIO,
        "filter": FILTER_GRAVE_CINE,
        "desc": "Tomás (Argentina) - Tono Narrativo de Crónica, Misterio e Historia"
    },
    {
        "id": "nativo_10_alex_peru_neutro_academico",
        "voice": "es-PE-AlexNeural",
        "rate": "+0%",
        "pitch": "-1Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_DOCUMENTAL,
        "desc": "Alex (Perú) - Pronunciación Neutra y Clara, Científica"
    },
    {
        "id": "nativo_11_salome_colombia_expresiva",
        "voice": "es-CO-SalomeNeural",
        "rate": "+1%",
        "pitch": "+0Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_DOCUMENTAL,
        "desc": "Salomé (Colombia) - Voz Cálida, Dulce y Educativa"
    },
    {
        "id": "nativo_12_sebastian_venezuela_shorts",
        "voice": "es-VE-SebastianNeural",
        "rate": "+10%",
        "pitch": "+0Hz",
        "text": TEXTO_VIRAL,
        "filter": FILTER_DINAMICO_SHORTS,
        "desc": "Sebastián (Venezuela) - Dinámico, Joven y Fluido para Shorts"
    },
    {
        "id": "nativo_13_lorenzo_chile_grave_sobrio",
        "voice": "es-CL-LorenzoNeural",
        "rate": "-2%",
        "pitch": "-3Hz",
        "text": TEXTO_DOCUMENTAL,
        "filter": FILTER_GRAVE_CINE,
        "desc": "Lorenzo (Chile) - Grave, Sobrio y Profesional"
    },
    {
        "id": "nativo_14_mateo_uruguay_reflexivo",
        "voice": "es-UY-MateoNeural",
        "rate": "-4%",
        "pitch": "-2Hz",
        "text": TEXTO_MISTERIO,
        "filter": FILTER_GRAVE_CINE,
        "desc": "Mateo (Uruguay) - Pausado, Misterioso y Cinematográfico"
    },
    {
        "id": "nativo_15_jorge_trailer_epico_profundo",
        "voice": "es-MX-JorgeNeural",
        "rate": "-5%",
        "pitch": "-4Hz",
        "text": TEXTO_MISTERIO,
        "filter": FILTER_GRAVE_CINE,
        "desc": "Jorge (México / Neutro) - Modo Trailer Épico Profundo (Ultra Grave)"
    }
]

async def run():
    print(f"Generando y masterizando {len(NUEVAS_VOCES)} nuevas voces nativas en español...\n")
    for s in NUEVAS_VOCES:
        raw_path = os.path.join(OUT_DIR, f"temp_{s['id']}.mp3")
        final_path = os.path.join(OUT_DIR, f"{s['id']}.mp3")
        
        print(f"-> Generando: {s['desc']} ({s['voice']})...")
        comm = edge_tts.Communicate(s["text"], s["voice"], rate=s["rate"], pitch=s["pitch"])
        await comm.save(raw_path)
        
        cmd = [FFMPEG, "-y", "-i", raw_path, "-af", s["filter"], "-b:a", "192k", final_path]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if os.path.exists(raw_path):
            os.remove(raw_path)
        print(f"   [OK] Guardado: muestras_voces/{s['id']}.mp3")
        
    print("\n¡Todas las 10 nuevas muestras nativas han sido generadas y masterizadas!")

if __name__ == "__main__":
    asyncio.run(run())
