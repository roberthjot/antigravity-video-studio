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

# Frases con redacción nativa y signos de puntuación pensados para pausas humanas
TEXTO_DOCUMENTAL = (
    "En las profundidades del océano Atlántico... la ingeniería humana enfrenta su mayor desafío. "
    "Gigantes de acero capaces de resistir olas de más de treinta metros, navegando hacia lo desconocido. "
    "Hoy descubriremos cómo estas colosales estructuras logran desafiar a la naturaleza."
)

TEXTO_SHORTS = (
    "¿Sabías que un barco moderno puede transportar más de veinte mil contenedores? "
    "Su motor es tan gigante como un edificio de cuatro pisos... y genera más de cien mil caballos de fuerza. "
    "¡Una auténtica bestia de los mares!"
)

# Filtro de Masterización de Estudio de Grabación (Broadcast Vocal Chain):
# - highpass: limpia frecuencias graves innecesarias por debajo de 75Hz (evita ruido sordo)
# - equalizer a 180Hz: añade calor y resonancia de caja torácica (+3.5dB)
# - equalizer a 3200Hz: añade presencia, aire y brillo a la articulación (+2.2dB)
# - acompressor: comprime la dinámica para nivelar picos y dar sonido de locución de radio/cine
# - alimiter: techo de -1dB para evitar distorsión digital
vocal_filter = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

SAMPLES = [
    {
        "id": "nativo_01_alvaro_espana_estudio",
        "voice": "es-ES-AlvaroNeural",
        "rate": "-2%",
        "pitch": "-2Hz",
        "text": TEXTO_DOCUMENTAL,
        "desc": "Álvaro (España) - Masterizado estilo Discovery Channel"
    },
    {
        "id": "nativo_02_jorge_mexico_estudio",
        "voice": "es-MX-JorgeNeural",
        "rate": "+2%",
        "pitch": "-1Hz",
        "text": TEXTO_DOCUMENTAL,
        "desc": "Jorge (México / Neutro) - Masterizado estilo Documental Latino Potente"
    },
    {
        "id": "nativo_03_elvira_espana_estudio",
        "voice": "es-ES-ElviraNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
        "text": TEXTO_DOCUMENTAL,
        "desc": "Elvira (España) - Masterizada Narración Femenina BBC"
    },
    {
        "id": "nativo_04_dalia_mexico_shorts",
        "voice": "es-MX-DaliaNeural",
        "rate": "+12%",
        "pitch": "+0Hz",
        "text": TEXTO_SHORTS,
        "desc": "Dalia (México) - Masterizada Dinámica para Shorts / Reels"
    },
    {
        "id": "nativo_05_gonzalo_colombia_estudio",
        "voice": "es-CO-GonzaloNeural",
        "rate": "+0%",
        "pitch": "-3Hz",
        "text": TEXTO_DOCUMENTAL,
        "desc": "Gonzalo (Colombia) - Masterizado Calidez y Proximidad"
    }
]

async def run_generation():
    print("Iniciando generación y masterización de voces nativas en español...\n")
    for s in SAMPLES:
        raw_path = os.path.join(OUT_DIR, f"temp_{s['id']}.mp3")
        final_path = os.path.join(OUT_DIR, f"{s['id']}.mp3")
        
        print(f"-> Generando: {s['desc']}...")
        comm = edge_tts.Communicate(s["text"], s["voice"], rate=s["rate"], pitch=s["pitch"])
        await comm.save(raw_path)
        
        cmd = [FFMPEG, "-y", "-i", raw_path, "-af", vocal_filter, "-b:a", "192k", final_path]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if os.path.exists(raw_path):
            os.remove(raw_path)
        print(f"   [OK] Guardado: muestras_voces/{s['id']}.mp3")
        
    print("\n¡Todas las muestras nativas masterizadas han sido creadas con éxito!")

if __name__ == "__main__":
    asyncio.run(run_generation())
