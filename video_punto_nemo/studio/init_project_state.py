import os
import json

STUDIO_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo\studio"
import sys
PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
sys.path.append(PROJECT_DIR)

from render_punto_nemo_8min_documentary import SCENES_8MIN

ACT_NAMES = {
    1: "Acto 1: Las Coordenadas del Aislamiento",
    2: "Acto 1: Las Coordenadas del Aislamiento",
    3: "Acto 1: Las Coordenadas del Aislamiento",
    4: "Acto 1: Las Coordenadas del Aislamiento",
    5: "Acto 2: Más Cerca del Espacio",
    6: "Acto 2: Más Cerca del Espacio",
    7: "Acto 2: Más Cerca del Espacio",
    8: "Acto 2: Más Cerca del Espacio",
    9: "Acto 3: El Sonido The Bloop y el Abismo",
    10: "Acto 3: El Sonido The Bloop y el Abismo",
    11: "Acto 3: El Sonido The Bloop y el Abismo",
    12: "Acto 3: El Sonido The Bloop y el Abismo",
    13: "Acto 4: El Desierto Biológico Marino",
    14: "Acto 4: El Desierto Biológico Marino",
    15: "Acto 4: El Desierto Biológico Marino",
    16: "Acto 5: La Ciudad de R'lyeh y Lovecraft",
    17: "Acto 5: La Ciudad de R'lyeh y Lovecraft",
    18: "Acto 5: La Ciudad de R'lyeh y Lovecraft",
    19: "Acto 6: Expediciones y Silencio en Alta Mar",
    20: "Acto 6: Expediciones y Silencio en Alta Mar",
    21: "Acto 6: Expediciones y Silencio en Alta Mar",
    22: "Acto 6: Expediciones y Silencio en Alta Mar",
    23: "Acto 7: La Gran Tumba de la Estación Espacial",
    24: "Acto 7: La Gran Tumba de la Estación Espacial",
    25: "Acto 7: La Gran Tumba de la Estación Espacial",
    26: "Acto 7: La Gran Tumba de la Estación Espacial",
    27: "Acto 7: La Gran Tumba de la Estación Espacial",
    28: "Acto 7: La Gran Tumba de la Estación Espacial",
    29: "Acto 8: El Último Abismo Inexplorado",
    30: "Acto 8: El Último Abismo Inexplorado",
    31: "Acto 8: El Último Abismo Inexplorado",
    32: "Acto 8: El Último Abismo Inexplorado",
}

# Todos los medios disponibles en la biblioteca local
ALL_MEDIA = [
    {"name": "00_intro_video_olas.webm", "type": "video", "title": "Video: Oleaje del Pacífico Sur"},
    {"name": "22_operaciones_alta_mar.webm", "type": "video", "title": "Video: Barco en Alta Mar"},
    {"name": "01_mapa_punto_nemo.jpg", "type": "image", "title": "Mapa Batimétrico Punto Nemo"},
    {"name": "02_mapa_polo_inaccesibilidad.jpg", "type": "image", "title": "Mapa Polar de Inaccesibilidad"},
    {"name": "03_tierra_pacifico_desde_iss.jpg", "type": "image", "title": "Tierra desde la Estación Espacial"},
    {"name": "04_astronauta_cupola.jpg", "type": "image", "title": "Astronauta en Cúpula ISS"},
    {"name": "05_estacion_espacial_mir.jpg", "type": "image", "title": "Estación Espacial Rusa Mir"},
    {"name": "06_carguero_progress.jpg", "type": "image", "title": "Nave de Carga Progress"},
    {"name": "07_reingreso_atmosferico_fuego.jpg", "type": "image", "title": "Reentrada Ígnea a la Atmósfera"},
    {"name": "09_bloop_espectrograma.jpg", "type": "image", "title": "Espectrograma de The Bloop"},
    {"name": "10_hidrofono_submarino.jpg", "type": "image", "title": "Hidrófono Submarino NOAA"},
    {"name": "12_iceberg_antartida_criosismo.jpg", "type": "image", "title": "Criosismo de Hielo Antártico"},
    {"name": "15_submarino_profundidades.jpg", "type": "image", "title": "Submarino en el Abismo"},
    {"name": "16_cthulhu_monstruo_marino.jpg", "type": "image", "title": "Monstruo Abisal / Lovecraft"},
    {"name": "18_criatura_abisal_mitologia.jpg", "type": "image", "title": "Criatura Abisal de las Sombras"},
    {"name": "19_estacion_espacial_internacional.jpg", "type": "image", "title": "Estación Espacial Internacional ISS"},
    {"name": "21_atardecer_dorado_pacifico.jpg", "type": "image", "title": "Atardecer Dorado en el Océano"},
    {"name": "23_hielo_polar_antartico.jpg", "type": "image", "title": "Hielo Polar Antártico"},
    {"name": "24_horizonte_vasto_atardecer.jpg", "type": "image", "title": "Horizonte Vasto Oceánico"},
    {"name": "25_navegacion_sigilo_radar.jpg", "type": "image", "title": "Radar de Navegación Marina"}
]

# Sugerencias contextuales de candidatos según el tema de cada escena
CATEGORIES = {
    "ocean": ["00_intro_video_olas.webm", "22_operaciones_alta_mar.webm", "21_atardecer_dorado_pacifico.jpg", "24_horizonte_vasto_atardecer.jpg"],
    "map": ["01_mapa_punto_nemo.jpg", "02_mapa_polo_inaccesibilidad.jpg", "03_tierra_pacifico_desde_iss.jpg", "25_navegacion_sigilo_radar.jpg"],
    "space": ["04_astronauta_cupola.jpg", "03_tierra_pacifico_desde_iss.jpg", "06_carguero_progress.jpg", "05_estacion_espacial_mir.jpg", "19_estacion_espacial_internacional.jpg", "07_reingreso_atmosferico_fuego.jpg"],
    "reentry": ["07_reingreso_atmosferico_fuego.jpg", "06_carguero_progress.jpg", "05_estacion_espacial_mir.jpg", "19_estacion_espacial_internacional.jpg"],
    "bloop": ["10_hidrofono_submarino.jpg", "09_bloop_espectrograma.jpg", "15_submarino_profundidades.jpg", "12_iceberg_antartida_criosismo.jpg"],
    "iceberg": ["12_iceberg_antartida_criosismo.jpg", "23_hielo_polar_antartico.jpg", "15_submarino_profundidades.jpg"],
    "desert": ["25_navegacion_sigilo_radar.jpg", "03_tierra_pacifico_desde_iss.jpg", "24_horizonte_vasto_atardecer.jpg", "21_atardecer_dorado_pacifico.jpg"],
    "lovecraft": ["16_cthulhu_monstruo_marino.jpg", "18_criatura_abisal_mitologia.jpg", "15_submarino_profundidades.jpg", "24_horizonte_vasto_atardecer.jpg"],
    "abyss": ["15_submarino_profundidades.jpg", "25_navegacion_sigilo_radar.jpg", "21_atardecer_dorado_pacifico.jpg", "00_intro_video_olas.webm"]
}

SCENE_THEMES = {
    1: "ocean", 2: "map", 3: "map", 4: "space",
    5: "space", 6: "space", 7: "reentry", 8: "reentry",
    9: "bloop", 10: "bloop", 11: "bloop", 12: "iceberg",
    13: "desert", 14: "desert", 15: "desert",
    16: "lovecraft", 17: "lovecraft", 18: "lovecraft",
    19: "ocean", 20: "ocean", 21: "desert", 22: "ocean",
    23: "space", 24: "reentry", 25: "space", 26: "space",
    27: "reentry", 28: "reentry", 29: "iceberg", 30: "abyss",
    31: "ocean", 32: "ocean"
}

SFX_OPTIONS = [
    {"id": None, "name": "Sin SFX"},
    {"id": "ocean_surge.wav", "name": "Oleaje y Viento Marino"},
    {"id": "telemetry_beep.wav", "name": "Radar y Telemetría"},
    {"id": "radio_squelch.wav", "name": "Radio de Astronautas (ISS)"},
    {"id": "reentry_roar.wav", "name": "Rugido de Reingreso Atmosférico"},
    {"id": "sonar_ping.wav", "name": "Sonar Submarino (NOAA)"},
    {"id": "deep_bloop.wav", "name": "Frecuencia Sub-Grave (The Bloop)"},
    {"id": "ice_crack.wav", "name": "Criosismo Antártico (Hielo)"},
    {"id": "cinematic_braam.wav", "name": "Impacto de Suspenso Cósmico"}
]

MOTION_OPTIONS = [
    {"id": "zoom_in", "name": "Zoom In Suave (Acercar)"},
    {"id": "zoom_out", "name": "Zoom Out (Alejar / Revelar)"},
    {"id": "pan_right", "name": "Panorámica Derecha (Barrido)"},
    {"id": "pan_left", "name": "Panorámica Izquierda (Barrido)"},
    {"id": "drift_up_right", "name": "Drift Diagonal Arriba"},
    {"id": "drift_down_left", "name": "Drift Diagonal Abajo"}
]

from render_monetizable_8min import SCENES

scenes_state = []
for sc in SCENES:
    sid = sc["id"]
    theme = SCENE_THEMES.get(sid, "ocean")
    suggested_names = CATEGORIES.get(theme, CATEGORIES["ocean"])
    
    # Asegurar que el actual esté primero en candidatos
    selected_name = sc["media"]
    candidate_names = [selected_name] + [m for m in suggested_names if m != selected_name]
    
    # Formatear candidatos con metadata
    candidates = []
    for cname in candidate_names:
        m_meta = next((m for m in ALL_MEDIA if m["name"] == cname), {
            "name": cname, "type": "video" if cname.endswith((".webm", ".mp4")) else "image", "title": cname
        })
        candidates.append(m_meta)

    sfx_val = sc["sfx"]["file"] if sc.get("sfx") else None
    
    scenes_state.append({
        "id": sid,
        "act": ACT_NAMES.get(sid, f"Acto {(sid-1)//4 + 1}"),
        "text": SCENES_8MIN[sid - 1]["text"],
        "media": selected_name,
        "is_video": sc.get("is_video", False),
        "motion": sc.get("motion", "zoom_in"),
        "sfx": sfx_val,
        "overlay": sc.get("overlay", None),
        "candidates": candidates
    })

project_state = {
    "title": "El Punto Nemo: El Lugar Más Aislado del Planeta",
    "total_scenes": len(scenes_state),
    "soundtrack": "soundtrack_dinamico_8min.mp3",
    "voice": "es-MX-JorgeNeural",
    "resolution": "1920x1080",
    "scenes": scenes_state,
    "library": ALL_MEDIA,
    "sfx_options": SFX_OPTIONS,
    "motion_options": MOTION_OPTIONS
}

out_file = os.path.join(STUDIO_DIR, "project_state.json")
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(project_state, f, indent=2, ensure_ascii=False)

print(f"Project state initialized with {len(scenes_state)} scenes in {out_file}")
