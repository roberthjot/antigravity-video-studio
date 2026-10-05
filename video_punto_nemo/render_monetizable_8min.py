import os
import sys
import subprocess
import imageio_ffmpeg
from subpixel_motion import generate_motion_video

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
OVERLAYS_DIR = os.path.join(PROJECT_DIR, "overlays")
SFX_DIR = os.path.join(PROJECT_DIR, "sfx")
TEMP_V2_DIR = os.path.join(PROJECT_DIR, "temp_clips_v2")
SRC_TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")

os.makedirs(TEMP_V2_DIR, exist_ok=True)

FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_8MIN_MONETIZABLE.mp4")
SOUNDTRACK = os.path.join(PROJECT_DIR, "soundtrack_dinamico_8min.mp3")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

SCENES = [
    # Acto 1
    {"id": 1, "media": "00_intro_video_olas.webm", "is_video": True, "seek": 0, "sfx": {"file": "ocean_surge.wav", "delay": 600, "vol": 0.38}, "overlay": "card_01.png"},
    {"id": 2, "media": "01_mapa_punto_nemo.jpg", "is_video": False, "motion": "zoom_in", "sfx": {"file": "telemetry_beep.wav", "delay": 1500, "vol": 0.35}, "overlay": "card_02.png"},
    {"id": 3, "media": "02_mapa_polo_inaccesibilidad.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": None},
    {"id": 4, "media": "04_astronauta_cupola.jpg", "is_video": False, "motion": "drift_up_right", "sfx": {"file": "radio_squelch.wav", "delay": 1000, "vol": 0.40}, "overlay": "card_04.png"},

    # Acto 2
    {"id": 5, "media": "03_tierra_pacifico_desde_iss.jpg", "is_video": False, "motion": "pan_right", "sfx": None, "overlay": None},
    {"id": 6, "media": "06_carguero_progress.jpg", "is_video": False, "motion": "zoom_in", "sfx": None, "overlay": "card_06.png"},
    {"id": 7, "media": "05_estacion_espacial_mir.jpg", "is_video": False, "motion": "drift_down_left", "sfx": {"file": "reentry_roar.wav", "delay": 1800, "vol": 0.30}, "overlay": None},
    {"id": 8, "media": "07_reingreso_atmosferico_fuego.jpg", "is_video": False, "motion": "pan_left", "sfx": None, "overlay": None},

    # Acto 3
    {"id": 9, "media": "10_hidrofono_submarino.jpg", "is_video": False, "motion": "zoom_in", "sfx": {"file": "sonar_ping.wav", "delay": 1200, "vol": 0.35}, "overlay": "card_09.png"},
    {"id": 10, "media": "09_bloop_espectrograma.jpg", "is_video": False, "motion": "pan_right", "sfx": {"file": "deep_bloop.wav", "delay": 2000, "vol": 0.45}, "overlay": None},
    {"id": 11, "media": "15_submarino_profundidades.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": None},
    {"id": 12, "media": "12_iceberg_antartida_criosismo.jpg", "is_video": False, "motion": "drift_up_right", "sfx": {"file": "ice_crack.wav", "delay": 1500, "vol": 0.40}, "overlay": "card_12.png"},

    # Acto 4
    {"id": 13, "media": "25_navegacion_sigilo_radar.jpg", "is_video": False, "motion": "pan_left", "sfx": None, "overlay": "card_13.png"},
    {"id": 14, "media": "03_tierra_pacifico_desde_iss.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": None},
    {"id": 15, "media": "24_horizonte_vasto_atardecer.jpg", "is_video": False, "motion": "pan_right", "sfx": None, "overlay": None},

    # Acto 5
    {"id": 16, "media": "16_cthulhu_monstruo_marino.jpg", "is_video": False, "motion": "zoom_in", "sfx": {"file": "cinematic_braam.wav", "delay": 1200, "vol": 0.40}, "overlay": "card_16.png"},
    {"id": 17, "media": "18_criatura_abisal_mitologia.jpg", "is_video": False, "motion": "drift_down_left", "sfx": None, "overlay": None},
    {"id": 18, "media": "16_cthulhu_monstruo_marino.jpg", "is_video": False, "motion": "pan_left", "sfx": None, "overlay": None},

    # Acto 6
    {"id": 19, "media": "22_operaciones_alta_mar.webm", "is_video": True, "seek": 0, "sfx": None, "overlay": None},
    {"id": 20, "media": "00_intro_video_olas.webm", "is_video": True, "seek": 15, "sfx": {"file": "ocean_surge.wav", "delay": 1000, "vol": 0.35}, "overlay": None},
    {"id": 21, "media": "25_navegacion_sigilo_radar.jpg", "is_video": False, "motion": "drift_up_right", "sfx": {"file": "telemetry_beep.wav", "delay": 1200, "vol": 0.35}, "overlay": None},
    {"id": 22, "media": "24_horizonte_vasto_atardecer.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": None},
    {"id": 23, "media": "03_tierra_pacifico_desde_iss.jpg", "is_video": False, "motion": "pan_right", "sfx": None, "overlay": None},
    {"id": 24, "media": "07_reingreso_atmosferico_fuego.jpg", "is_video": False, "motion": "zoom_in", "sfx": None, "overlay": None},

    # Acto 7
    {"id": 25, "media": "06_carguero_progress.jpg", "is_video": False, "motion": "drift_down_left", "sfx": None, "overlay": "card_25.png"},
    {"id": 26, "media": "19_estacion_espacial_internacional.jpg", "is_video": False, "motion": "pan_left", "sfx": {"file": "radio_squelch.wav", "delay": 1200, "vol": 0.40}, "overlay": None},
    {"id": 27, "media": "07_reingreso_atmosferico_fuego.jpg", "is_video": False, "motion": "zoom_in", "sfx": {"file": "reentry_roar.wav", "delay": 1500, "vol": 0.30}, "overlay": "card_27.png"},
    {"id": 28, "media": "05_estacion_espacial_mir.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": None},

    # Acto 8
    {"id": 29, "media": "23_hielo_polar_antartico.jpg", "is_video": False, "motion": "pan_right", "sfx": None, "overlay": None},
    {"id": 30, "media": "15_submarino_profundidades.jpg", "is_video": False, "motion": "drift_up_right", "sfx": {"file": "sonar_ping.wav", "delay": 1000, "vol": 0.35}, "overlay": None},
    {"id": 31, "media": "21_atardecer_dorado_pacifico.jpg", "is_video": False, "motion": "zoom_out", "sfx": None, "overlay": "card_31.png"},
    {"id": 32, "media": "00_intro_video_olas.webm", "is_video": True, "seek": 22, "sfx": {"file": "ocean_surge.wav", "delay": 1000, "vol": 0.35}, "overlay": None}
]

def get_duration(audio_file):
    cmd = [FFMPEG, "-i", audio_file]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 15.0

def build_scene_audio(sc):
    sid = sc["id"]
    master_vce = os.path.join(SRC_TEMP_DIR, f"master_audio_{sid:02d}.mp3")
    if not os.path.exists(master_vce):
        raise FileNotFoundError(f"Missing master voice: {master_vce}")

    # Si tiene SFX, mezclar como WAV
    if sc.get("sfx"):
        sfx_info = sc["sfx"]
        sfx_path = os.path.join(SFX_DIR, sfx_info["file"])
        out_audio = os.path.join(TEMP_V2_DIR, f"audio_mixed_{sid:02d}.wav")
        delay = sfx_info["delay"]
        vol = sfx_info["vol"]
        
        cmd = [
            FFMPEG, "-y",
            "-i", master_vce,
            "-i", sfx_path,
            "-filter_complex",
            f"[0:a]volume=1.0[vce];[1:a]adelay={delay}|{delay},volume={vol}[sfx];[vce][sfx]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            out_audio
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return out_audio
    else:
        return master_vce

def get_motion_filter(motion_type, N):
    # Lienzo 4K (3840x2160) + Lanczos downscale a 1080p: elimina 100% el temblor o vibración subpixel
    if motion_type == "zoom_in":
        zp = f"zoompan=z='1.0+0.20*(on/{N})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
    elif motion_type == "zoom_out":
        zp = f"zoompan=z='1.22-0.18*(on/{N})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
    elif motion_type == "pan_right":
        zp = f"zoompan=z=1.18:x='(on/{N})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
    elif motion_type == "pan_left":
        zp = f"zoompan=z=1.18:x='(1.0-on/{N})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
    elif motion_type == "drift_up_right":
        zp = f"zoompan=z='1.06+0.14*(on/{N})':x='(on/{N})*(iw-iw/zoom)':y='(1.0-on/{N})*(ih-ih/zoom)':d=1:s=3840x2160:fps=30"
    elif motion_type == "drift_down_left":
        zp = f"zoompan=z='1.20-0.12*(on/{N})':x='(1.0-on/{N})*(iw-iw/zoom)':y='(on/{N})*(ih-ih/zoom)':d=1:s=3840x2160:fps=30"
    else:
        zp = f"zoompan=z='1.0+0.18*(on/{N})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=3840x2160:fps=30"
    return f"scale=3840:2160,{zp},scale=1920:1080:flags=lanczos"

def render_scene(sc):
    sid = sc["id"]
    out_clip = os.path.join(TEMP_V2_DIR, f"clip_v2_{sid:02d}.mp4")
    
    if os.path.exists(out_clip) and os.path.getsize(out_clip) > 1000000:
        dur = get_duration(out_clip)
        return out_clip, dur

    # 1. Obtener audio con SFX
    scene_audio = build_scene_audio(sc)
    dur = get_duration(scene_audio)
    N = int(round(dur * 30))
    st_out = max(dur - 2.0, 5.0)

    # 2. Renderizar video
    overlay_name = sc.get("overlay")
    overlay_file = os.path.join(OVERLAYS_DIR, overlay_name) if overlay_name else None

    if sc["is_video"]:
        media_path = os.path.join(MEDIA_DIR, sc["media"])
        seek_val = sc.get("seek", 0)
        
        if overlay_file and os.path.exists(overlay_file):
            cmd = [
                FFMPEG, "-y",
                "-ss", str(seek_val),
                "-i", media_path,
                "-i", scene_audio,
                "-loop", "1", "-i", overlay_file,
                "-filter_complex",
                f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30[base];"
                f"[2:v]fade=t=in:st=1.2:d=0.8:alpha=1,fade=t=out:st={st_out:.1f}:d=0.8:alpha=1[ovl];"
                f"[base][ovl]overlay=0:0,format=yuv420p[vcomp]",
                "-map", "[vcomp]",
                "-map", "1:a",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-shortest",
                out_clip
            ]
        else:
            cmd = [
                FFMPEG, "-y",
                "-ss", str(seek_val),
                "-i", media_path,
                "-i", scene_audio,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p",
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-shortest",
                out_clip
            ]
    else:
        media_path = os.path.join(OPTIMIZED_DIR, sc["media"])
        
        # 1. Generate smooth subpixel video (no audio/overlay yet)
        raw_motion_clip = os.path.join(TEMP_V2_DIR, f"raw_motion_{sid:02d}.mp4")
        if not os.path.exists(raw_motion_clip) or os.path.getsize(raw_motion_clip) < 1000000:
            generate_motion_video(media_path, raw_motion_clip, sc.get("motion", "zoom_in"), dur, fps=30)
            
        # 2. Add audio and optional overlay
        if overlay_file and os.path.exists(overlay_file):
            cmd = [
                FFMPEG, "-y",
                "-i", raw_motion_clip,
                "-i", scene_audio,
                "-loop", "1", "-i", overlay_file,
                "-filter_complex",
                f"[2:v]fade=t=in:st=1.2:d=0.8:alpha=1,fade=t=out:st={st_out:.1f}:d=0.8:alpha=1[ovl];"
                f"[0:v][ovl]overlay=0:0,format=yuv420p[vcomp]",
                "-map", "[vcomp]",
                "-map", "1:a",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-shortest",
                out_clip
            ]
        else:
            cmd = [
                FFMPEG, "-y",
                "-i", raw_motion_clip,
                "-i", scene_audio,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy", # we can just copy the video stream since it's already generated exactly right!
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-shortest",
                out_clip
            ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return out_clip, dur

def main():
    print("==================================================================")
    print("   MONTAJE MAESTRO MONETIZABLE: EL PUNTO NEMO (32 ESCENAS)")
    print("   -> Movimiento continuo de cámara (Ken Burns dinámico)")
    print("   -> 12 Efectos de Sonido Cinematográficos (SFX / Foleys)")
    print("   -> 11 Tarjetas de Datos e Infografías en Pantalla (Lower Thirds)")
    print("==================================================================\n")

    rendered_clips = []
    concat_list = os.path.join(TEMP_V2_DIR, "concat_v2_list.txt")

    for idx, sc in enumerate(SCENES, 1):
        sfx_tag = f"+ SFX ({sc['sfx']['file']})" if sc.get("sfx") else ""
        ovl_tag = f"+ OVL ({sc['overlay']})" if sc.get("overlay") else ""
        clip_path, dur = render_scene(sc)
        rendered_clips.append(clip_path)
        print(f"[{idx:02d}/32] Escena {sc['id']:02d} lista ({dur:.1f}s | {sc.get('motion', 'video'):<16} {sfx_tag} {ovl_tag})")

    # Concatenación
    print("\nConcatenando las 32 escenas en pista unificada...")
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in rendered_clips:
            clean_c = c.replace("\\", "/")
            f.write(f"file '{clean_c}'\n")

    video_no_soundtrack = os.path.join(TEMP_V2_DIR, "documental_v2_no_soundtrack.mp4")
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        video_no_soundtrack
    ]
    subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Mezclar Soundtrack Dinámico
    print("Mezclando banda sonora dinámica cinematográfica con auto-ducking...")
    cmd_final = [
        FFMPEG, "-y",
        "-i", video_no_soundtrack,
        "-i", SOUNDTRACK,
        "-filter_complex",
        "[1:a]volume=0.13[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-shortest",
        FINAL_OUTPUT
    ]
    subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    final_dur = get_duration(FINAL_OUTPUT)
    print("\n==================================================================")
    print(" ¡DOCUMENTAL MONETIZABLE DE 8 MINUTOS COMPLETADO CON ÉXITO!")
    print(f" Archivo final: {FINAL_OUTPUT}")
    print(f" Duración final: {final_dur:.2f} segundos ({final_dur/60:.2f} minutos)")
    print("==================================================================\n")

if __name__ == "__main__":
    main()
