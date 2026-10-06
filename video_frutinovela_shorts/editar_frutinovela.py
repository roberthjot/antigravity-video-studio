import os
import subprocess
import re
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
folder = os.path.expanduser('~/Downloads/fruta-editor')
out_video = os.path.join(folder, 'CAPITULO_2_FINAL.mp4')
temp_dir = os.path.join(folder, 'temp_edit')
os.makedirs(temp_dir, exist_ok=True)

order = [
    'k1.mp4', 'k2.mp4', 'k3.mp4', 'k4.mp4', 'k5.mp4',
    'k5.5.mp4', 'k6.mp4', 'k7.mp4', 'k8.mp4', 'k10.mp4',
    'k11.mp4', 'k12.mp4', 'k13.mp4', 'k14.mp4', 'k15.mp4'
]

print("=== 1. ANALIZANDO Y RECORTANDO SILENCIOS DE CADA CLIP ===")
trimmed_clips = []

for idx, f in enumerate(order):
    inp = os.path.join(folder, f)
    out_trimmed = os.path.join(temp_dir, f'trimmed_{idx:02d}_{f}')
    
    # Obtener duracion total
    cmd_d = [ffmpeg, '-i', inp]
    r_d = subprocess.run(cmd_d, stderr=subprocess.PIPE, text=True)
    m = re.search(r'Duration:\s*(\d+:\d+:\d+\.\d+)', r_d.stderr)
    dur_str = m.group(1) if m else '00:00:06.00'
    p = dur_str.split(':')
    total_dur = float(p[0])*3600 + float(p[1])*60 + float(p[2])
    
    # Detectar silencios
    cmd_s = [ffmpeg, '-i', inp, '-af', 'silencedetect=n=-28dB:d=0.25', '-f', 'null', '-']
    res_s = subprocess.run(cmd_s, stderr=subprocess.PIPE, text=True)
    
    s_starts = [float(x) for x in re.findall(r'silence_start:\s*([\d\.]+)', res_s.stderr)]
    s_ends = [float(x) for x in re.findall(r'silence_end:\s*([\d\.]+)', res_s.stderr)]
    
    # Si hay silencio al principio (antes de los primeros 0.1s)
    start_trim = 0.0
    if s_starts and s_ends and s_starts[0] <= 0.08:
        # dejar 0.05s de aire antes de que hable para no cortar la primera consonante
        start_trim = max(0.0, s_ends[0] - 0.06)
        
    # Si hay silencio muerto al final
    end_trim = total_dur
    if s_starts and s_starts[-1] >= total_dur - 1.8:
        # dejar 0.1s de aire al final de la voz
        end_trim = min(total_dur, s_starts[-1] + 0.12)
        
    clip_dur = end_trim - start_trim
    print(f"[{idx+1}/15] {f}: Total={total_dur:.2f}s -> Recorte: {start_trim:.2f}s a {end_trim:.2f}s (Duración útil: {clip_dur:.2f}s)")
    
    # Recortar video y audio sincronizados con re-encoding rapido ultrafast
    cmd_cut = [
        ffmpeg, '-y',
        '-ss', str(start_trim),
        '-to', str(end_trim),
        '-i', inp,
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
        '-c:a', 'aac', '-b:a', '192k',
        out_trimmed
    ]
    subprocess.run(cmd_cut, capture_output=True, check=True)
    trimmed_clips.append(out_trimmed)

print("\n=== 2. CONCATENANDO LOS 15 CLIPS RECORTADOS ===")
concat_list_file = os.path.join(temp_dir, 'concat_list.txt')
with open(concat_list_file, 'w', encoding='utf-8') as f:
    for c in trimmed_clips:
        # Formato seguro para ffmpeg
        clean_path = c.replace('\\', '/')
        f.write(f"file '{clean_path}'\n")

concat_video = os.path.join(temp_dir, 'video_concatenado.mp4')
cmd_concat = [
    ffmpeg, '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concat_list_file,
    '-c', 'copy',
    concat_video
]
subprocess.run(cmd_concat, capture_output=True, check=True)

# Obtener duracion del video concatenado
r_v = subprocess.run([ffmpeg, '-i', concat_video], stderr=subprocess.PIPE, text=True)
m_v = re.search(r'Duration:\s*(\d+:\d+:\d+\.\d+)', r_v.stderr)
v_dur_str = m_v.group(1) if m_v else '00:01:30.00'
p_v = v_dur_str.split(':')
v_total_dur = float(p_v[0])*3600 + float(p_v[1])*60 + float(p_v[2])
print(f"Duración total del video concatenado: {v_total_dur:.2f} segundos")

print("\n=== 3. MEZCLANDO MÚSICA DE FONDO SIN CAMBIAR VOLUMEN ===")
music_file = os.path.join(folder, 'music-frutas.mp3')

# Filtro de audio: amix manteniendo volumen original con fadeout al final del video
# y limitador suave para evitar distorsiones
fade_start = max(0.0, v_total_dur - 2.5)
filter_complex = (
    f"[1:a]afade=t=out:st={fade_start:.2f}:d=2.5[bgm];"
    f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
)

cmd_final = [
    ffmpeg, '-y',
    '-i', concat_video,
    '-i', music_file,
    '-filter_complex', filter_complex,
    '-map', '0:v',
    '-map', '[aout]',
    '-c:v', 'copy',
    '-c:a', 'aac', '-b:a', '192k',
    '-t', str(v_total_dur),
    out_video
]

res_final = subprocess.run(cmd_final, capture_output=True, text=True)
if res_final.returncode == 0:
    print(f"\n✅ ¡ÉXITO TOTAL! Video final creado en: {out_video}")
    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"Tamaño final: {size_mb:.2f} MB")
else:
    print("Error al mezclar:", res_final.stderr)
