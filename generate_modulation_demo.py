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

vocal_filter = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

# Comparación 1: Voz completamente PLANA (como viene por defecto, todo al mismo tono)
TEXTO_PLANO = (
    "Durante décadas, la tripulación del buque reportó anomalías extrañas en el radar. "
    "Nadie podía explicar cómo una masa de trescientas mil toneladas podía desvanecerse en cuestión de minutos. "
    "¿Qué fue lo que realmente ocurrió aquella noche en medio de la tormenta?"
)

# Comparación 2: La MISMA narración modulada por partes con cambios de tono y velocidad humana
SEGMENTOS_MODULADOS_ALVARO = [
    {
        "text": "Durante décadas... la tripulación del buque reportó anomalías extrañas en el radar.",
        "rate": "+2%",
        "pitch": "+1Hz",   # Tono ligeramente alto para iniciar y captar atención
        "pause_after": 0.35
    },
    {
        "text": "Nadie podía explicar... cómo una colosal estructura de trescientas mil toneladas... podía desvanecerse en cuestión de minutos.",
        "rate": "-6%",
        "pitch": "-4Hz",   # Tono mucho más grave y pausado: genera misterio y peso
        "pause_after": 0.50
    },
    {
        "text": "¿Qué fue lo que realmente ocurrió aquella noche... en medio de la tormenta?",
        "rate": "-1%",
        "pitch": "-1Hz",   # Curva interrogativa dramática
        "pause_after": 0.20
    }
]

SEGMENTOS_MODULADOS_JORGE = [
    {
        "text": "¡Presta atención a esto! En medio del océano, existe un punto donde ningún barco se atreve a navegar.",
        "rate": "+6%",
        "pitch": "+2Hz",   # Tono enérgico de gancho inicial
        "pause_after": 0.30
    },
    {
        "text": "Las profundidades aquí superan los seis mil metros. Y la presión es tan brutal... que destruiría un submarino en un segundo.",
        "rate": "-5%",
        "pitch": "-5Hz",   # Bajada a graves profundos: tensión y peligro
        "pause_after": 0.50
    },
    {
        "text": "Hoy conocerás a los colosos de acero... diseñados para desafiar este abismo.",
        "rate": "+0%",
        "pitch": "-2Hz",   # Tono concluyente con autoridad
        "pause_after": 0.20
    }
]

async def create_monotone():
    print("1. Creando muestra plana (sin modular tonos)...")
    raw_path = os.path.join(OUT_DIR, "temp_plano.mp3")
    final_path = os.path.join(OUT_DIR, "modulacion_01_alvaro_plano_sin_modular.mp3")
    comm = edge_tts.Communicate(TEXTO_PLANO, "es-ES-AlvaroNeural", rate="+0%", pitch="+0Hz")
    await comm.save(raw_path)
    cmd = [FFMPEG, "-y", "-i", raw_path, "-af", vocal_filter, "-b:a", "192k", final_path]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if os.path.exists(raw_path): os.remove(raw_path)
    print("   [OK] Guardado: modulacion_01_alvaro_plano_sin_modular.mp3")

async def create_modulated(voice, segments, out_name):
    print(f"2. Creando muestra modulada dinámicamente ({out_name})...")
    part_files = []
    for i, seg in enumerate(segments):
        p_raw = os.path.join(OUT_DIR, f"temp_{out_name}_part_{i}.mp3")
        comm = edge_tts.Communicate(seg["text"], voice, rate=seg["rate"], pitch=seg["pitch"])
        await comm.save(p_raw)
        part_files.append((p_raw, seg["pause_after"]))
    
    # Concatenar con silencios precisos
    concat_list_file = os.path.join(OUT_DIR, f"concat_{out_name}.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p_file, _ in part_files:
            f.write(f"file '{os.path.basename(p_file)}'\n")
            
    final_path = os.path.join(OUT_DIR, f"{out_name}.mp3")
    cmd = [
        FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-af", vocal_filter,
        "-b:a", "192k",
        final_path
    ]
    subprocess.run(cmd, cwd=OUT_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # Limpieza
    if os.path.exists(concat_list_file): os.remove(concat_list_file)
    for p_file, _ in part_files:
        if os.path.exists(p_file): os.remove(p_file)
    print(f"   [OK] Guardado: {out_name}.mp3")

async def main():
    await create_monotone()
    await create_modulated("es-ES-AlvaroNeural", SEGMENTOS_MODULADOS_ALVARO, "modulacion_02_alvaro_dinamica_cinematica")
    await create_modulated("es-MX-JorgeNeural", SEGMENTOS_MODULADOS_JORGE, "modulacion_03_jorge_latino_emocional")

if __name__ == "__main__":
    asyncio.run(main())
