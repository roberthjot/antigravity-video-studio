import os
from PIL import Image, ImageDraw, ImageFont

OVERLAYS_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo\overlays"
os.makedirs(OVERLAYS_DIR, exist_ok=True)

font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)
font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 21)

cards = {
    1: {
        "badge": "POLO OCEÁNICO DE INACCESIBILIDAD",
        "title": "EL PUNTO NEMO",
        "sub": "El rincón más solitario y aislado del planeta Tierra"
    },
    2: {
        "badge": "COORDENADAS GEOGRÁFICAS",
        "title": "48°52.6′S   123°23.6′W",
        "sub": "Océano Pacífico Sur · A 2,688 km de tierra firme"
    },
    4: {
        "badge": "AISLAMIENTO EXTREMO",
        "title": "LOS HUMANOS MÁS CERCANOS: EN ÓRBITA",
        "sub": "Estación Espacial Internacional (ISS) a ~415 km de altitud"
    },
    6: {
        "badge": "ZONA INTERNACIONAL DESIGNADA",
        "title": "SPOUA: ÁREA OCEÁNICA DESHABITADA",
        "sub": "Zona de reentrada y desorbitación segura de naves"
    },
    9: {
        "badge": "EXPEDIENTE NOAA · VERANO 1997",
        "title": 'EL MISTERIO ACÚSTICO: "THE BLOOP"',
        "sub": "Señal submarina de ultra baja frecuencia captada a +5,000 km"
    },
    12: {
        "badge": "RESOLUCIÓN CIENTÍFICA",
        "title": "CRIOSISMO POLAR ANTÁRTICO",
        "sub": "Fractura y colapso masivo de hielo resonando en el abismo"
    },
    13: {
        "badge": "OCEANOGRAFÍA DEL PACÍFICO",
        "title": "EL GIRO DEL PACÍFICO SUR",
        "sub": "Desierto biológico marino ultra-oligotrófico (sin nutrientes)"
    },
    16: {
        "badge": "COINCIDENCIA LITERARIA · H.P. LOVECRAFT",
        "title": "LA CIUDAD SUMERGIDA DE R'LYEH",
        "sub": "Ubicada en 1928 a solo unos cientos de km del Punto Nemo"
    },
    25: {
        "badge": "CRONOGRAMA ESPACIAL OFICIAL",
        "title": "DESTINO FINAL DE LA ISS: ENERO 2031",
        "sub": "Desorbitación y reingreso controlado de más de 400 toneladas"
    },
    27: {
        "badge": "CEMENTERIO ESPACIAL SUBMARINO",
        "title": "MÁS DE 263 NAVES ESPACIALES HUNDIDAS",
        "sub": "Estación Mir, 140+ cargueros Progress, Salyut y cápsulas ATV"
    },
    31: {
        "badge": "EXPEDICIÓN FINAL",
        "title": "EL ABISMO SILENCIOSO",
        "sub": "Profundidad media: 4,000 metros bajo el nivel del mar"
    }
}

for sid, info in cards.items():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    w_title = draw.textlength(info["title"], font=font_title)
    w_sub = draw.textlength(info["sub"], font=font_sub)
    w_badge = draw.textlength(info["badge"], font=font_badge)
    box_w = max(w_title, w_sub, w_badge) + 70
    box_w = max(box_w, 750)
    
    x0, y0 = 80, 830
    x1, y1 = x0 + box_w, y0 + 170
    
    # Dark glass rounded box with translucent border
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(11, 20, 36, 225), outline=(0, 229, 255, 180), width=2)
    # Cyan accent vertical bar
    draw.rounded_rectangle([x0 + 4, y0 + 14, x0 + 12, y1 - 14], radius=4, fill=(0, 229, 255, 255))
    
    # Texts
    draw.text((x0 + 30, y0 + 20), info["badge"], fill=(0, 229, 255, 255), font=font_badge)
    draw.text((x0 + 30, y0 + 58), info["title"], fill=(255, 255, 255, 255), font=font_title)
    draw.text((x0 + 30, y0 + 110), info["sub"], fill=(203, 213, 225, 255), font=font_sub)
    
    out_file = os.path.join(OVERLAYS_DIR, f"card_{sid:02d}.png")
    img.save(out_file, "PNG")

print(f"Successfully generated {len(cards)} broadcast graphic cards in overlays/")
