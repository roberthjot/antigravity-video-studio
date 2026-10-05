import os
import subprocess
import imageio_ffmpeg
from subpixel_motion import generate_motion_video

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
OVERLAYS_DIR = os.path.join(PROJECT_DIR, "overlays")
SFX_DIR = os.path.join(PROJECT_DIR, "sfx")
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
SOUNDTRACK = os.path.join(PROJECT_DIR, "soundtrack_dinamico_8min.mp3")
OUTPUT_TEST = os.path.join(PROJECT_DIR, "prueba_cinematica_suave_30s.mp4")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# =====================================================================
# TOMA 1: Astronauta en la Cúpula de la ISS mirando a la Tierra (11.6s)
# =====================================================================
vce4 = os.path.join(TEMP_DIR, "master_audio_04.mp3")
sfx4 = os.path.join(SFX_DIR, "radio_squelch.wav")
img4 = os.path.join(OPTIMIZED_DIR, "04_astronauta_cupola.jpg")
ovl4 = os.path.join(OVERLAYS_DIR, "card_04.png")
clip4 = os.path.join(TEMP_DIR, "cinematic_sc4.mp4")
raw4 = os.path.join(TEMP_DIR, "raw_subpixel_sc4.mp4")

dur4 = 11.6
print("Generando movimiento subpixel perfecto para Toma 1 (Astronauta)...")
generate_motion_video(img4, raw4, "zoom_in", dur4, fps=30)

audio4 = os.path.join(TEMP_DIR, "cinematic_audio4.wav")
subprocess.run([
    FFMPEG, "-y", "-i", vce4, "-i", sfx4,
    "-filter_complex", "[0:a]volume=1.0[vce];[1:a]adelay=1000|1000,volume=0.40[sfx];[vce][sfx]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]", audio4
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

subprocess.run([
    FFMPEG, "-y",
    "-i", raw4,
    "-i", audio4,
    "-loop", "1", "-i", ovl4,
    "-filter_complex",
    f"[2:v]fade=t=in:st=1.2:d=0.8:alpha=1,fade=t=out:st=8.0:d=0.8:alpha=1[ovl];[0:v][ovl]overlay=0:0,format=yuv420p[vcomp]",
    "-map", "[vcomp]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", clip4
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Toma 1 (Astronauta en Cúpula) lista.")

# =====================================================================
# TOMA 2: Reingreso de Nave Espacial en Llamas a la Atmósfera (12.7s)
# =====================================================================
vce8 = os.path.join(TEMP_DIR, "master_audio_08.mp3")
sfx8 = os.path.join(SFX_DIR, "reentry_roar.wav")
img8 = os.path.join(OPTIMIZED_DIR, "07_reingreso_atmosferico_fuego.jpg")
clip8 = os.path.join(TEMP_DIR, "cinematic_sc8.mp4")
raw8 = os.path.join(TEMP_DIR, "raw_subpixel_sc8.mp4")

dur8 = 12.7
print("Generando movimiento subpixel perfecto para Toma 2 (Reentrada Ígnea)...")
generate_motion_video(img8, raw8, "zoom_out", dur8, fps=30)

audio8 = os.path.join(TEMP_DIR, "cinematic_audio8.wav")
subprocess.run([
    FFMPEG, "-y", "-i", vce8, "-i", sfx8,
    "-filter_complex", "[0:a]volume=1.0[vce];[1:a]adelay=1500|1500,volume=0.35[sfx];[vce][sfx]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]", audio8
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

subprocess.run([
    FFMPEG, "-y",
    "-i", raw8,
    "-i", audio8,
    "-map", "0:v", "-map", "1:a",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", clip8
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Toma 2 (Reentrada Ígnea) lista.")

# =====================================================================
# TOMA 3: Submarino en el Abismo Oceánico con Luces (6.0s)
# =====================================================================
img15 = os.path.join(OPTIMIZED_DIR, "15_submarino_profundidades.jpg")
sfx15 = os.path.join(SFX_DIR, "sonar_ping.wav")
clip15 = os.path.join(TEMP_DIR, "cinematic_sc15.mp4")
raw15 = os.path.join(TEMP_DIR, "raw_subpixel_sc15.mp4")

dur15 = 6.0
print("Generando movimiento subpixel perfecto para Toma 3 (Submarino Abisal)...")
generate_motion_video(img15, raw15, "drift_up_right", dur15, fps=30)

subprocess.run([
    FFMPEG, "-y",
    "-i", raw15,
    "-i", sfx15,
    "-map", "0:v", "-map", "1:a",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-t", "6.0",
    clip15
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Toma 3 (Submarino Abisal) lista.")

# =====================================================================
# Concatenar las 3 tomas y mezclar con la banda sonora
# =====================================================================
concat_txt = os.path.join(TEMP_DIR, "cinematic_30s_list.txt")
c4 = clip4.replace("\\", "/")
c8 = clip8.replace("\\", "/")
c15 = clip15.replace("\\", "/")
with open(concat_txt, "w", encoding="utf-8") as f:
    f.write(f"file '{c4}'\n")
    f.write(f"file '{c8}'\n")
    f.write(f"file '{c15}'\n")

temp_raw = os.path.join(TEMP_DIR, "cinematic_30s_raw.mp4")
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", temp_raw
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

subprocess.run([
    FFMPEG, "-y",
    "-i", temp_raw,
    "-i", SOUNDTRACK,
    "-filter_complex",
    "[1:a]volume=0.13[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "0:v", "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", OUTPUT_TEST
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

size_mb = os.path.getsize(OUTPUT_TEST) / (1024*1024)
print(f"¡Video cinematográfico de 30s finalizado con éxito! {OUTPUT_TEST} ({size_mb:.2f} MB)")
