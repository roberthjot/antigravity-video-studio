import os
import subprocess
import imageio_ffmpeg

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
OVERLAYS_DIR = os.path.join(PROJECT_DIR, "overlays")
SFX_DIR = os.path.join(PROJECT_DIR, "sfx")
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
SOUNDTRACK = os.path.join(PROJECT_DIR, "soundtrack_dinamico_8min.mp3")
OUTPUT_TEST = os.path.join(PROJECT_DIR, "prueba_movimiento_suave_30s.mp4")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# 1. Escena 2: Zoom In con Tarjeta Gráfica y SFX de Telemetría
vce2 = os.path.join(TEMP_DIR, "master_audio_02.mp3")
sfx2 = os.path.join(SFX_DIR, "telemetry_beep.wav")
img2 = os.path.join(OPTIMIZED_DIR, "01_mapa_punto_nemo.jpg")
ovl2 = os.path.join(OVERLAYS_DIR, "card_02.png")
clip2 = os.path.join(TEMP_DIR, "test_sc2.mp4")

audio2 = os.path.join(TEMP_DIR, "test_audio2.wav")
subprocess.run([
    FFMPEG, "-y", "-i", vce2, "-i", sfx2,
    "-filter_complex", "[0:a]volume=1.0[vce];[1:a]adelay=1500|1500,volume=0.35[sfx];[vce][sfx]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "[aout]", audio2
], check=True)

dur2 = 11.5
N2 = int(round(dur2 * 30))
zp2 = f"zoompan=z='1.0+0.20*(on/{N2})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
motion2 = f"scale=3840:2160,{zp2},scale=1920:1080:flags=lanczos"

subprocess.run([
    FFMPEG, "-y",
    "-framerate", "30", "-loop", "1", "-i", img2,
    "-i", audio2,
    "-loop", "1", "-i", ovl2,
    "-filter_complex",
    f"[0:v]{motion2}[base];[2:v]fade=t=in:st=1.2:d=0.8:alpha=1,fade=t=out:st=8.0:d=0.8:alpha=1[ovl];[base][ovl]overlay=0:0,format=yuv420p[vcomp]",
    "-map", "[vcomp]", "-map", "1:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", clip2
], check=True)
print("Escena 2 (Zoom In) generada con éxito.")

# 2. Escena 3: Zoom Out continuo
vce3 = os.path.join(TEMP_DIR, "master_audio_03.mp3")
img3 = os.path.join(OPTIMIZED_DIR, "02_mapa_polo_inaccesibilidad.jpg")
clip3 = os.path.join(TEMP_DIR, "test_sc3.mp4")

dur3 = 17.0
N3 = int(round(dur3 * 30))
zp3 = f"zoompan=z='1.24-0.20*(on/{N3})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
motion3 = f"scale=3840:2160,{zp3},scale=1920:1080:flags=lanczos"

subprocess.run([
    FFMPEG, "-y",
    "-framerate", "30", "-loop", "1", "-i", img3,
    "-i", vce3,
    "-vf", f"{motion3},format=yuv420p",
    "-map", "0:v", "-map", "1:a",
    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", clip3
], check=True)
print("Escena 3 (Zoom Out) generada con éxito.")

# 3. Concatenación y mezcla de música
concat_txt = os.path.join(TEMP_DIR, "test_30s_list.txt")
clean_c2 = clip2.replace("\\", "/")
clean_c3 = clip3.replace("\\", "/")
with open(concat_txt, "w") as f:
    f.write(f"file '{clean_c2}'\n")
    f.write(f"file '{clean_c3}'\n")

temp_concat = os.path.join(TEMP_DIR, "test_30s_raw.mp4")
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", temp_concat
], check=True)

subprocess.run([
    FFMPEG, "-y",
    "-i", temp_concat,
    "-i", SOUNDTRACK,
    "-filter_complex",
    "[1:a]volume=0.13[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
    "-map", "0:v", "-map", "[aout]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
    "-shortest", OUTPUT_TEST
], check=True)

size_mb = os.path.getsize(OUTPUT_TEST) / (1024*1024)
print(f"¡Prueba de 30 segundos finalizada con éxito! Archivo: {OUTPUT_TEST} ({size_mb:.2f} MB)")
