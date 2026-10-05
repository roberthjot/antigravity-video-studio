# 🎬 Antigravity Video Studio & Documentary Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Antigravity Video Studio** es una suite automatizada de producción y montaje documental de alta calidad para YouTube y plataformas de video. Combina un **estudio web interactivo** (FastAPI + Vue 3) para la curaduría visual y sonora con un **motor de renderizado cinemático** de precisión matemática capaz de producir documentales de formato largo (8+ minutos) listos para monetización.

---

## 🌟 Características Principales

### 1. 🎥 Motor de Cámara Subpíxel Anti-Jitter (`subpixel_motion.py`)
- **Problema resuelto:** Los filtros tradicionales como `zoompan` de FFmpeg truncan las coordenadas de recorte ($x, y$) a números enteros en cada fotograma. En paneos lentos y sutiles de estilo documental, esto provoca una molesta vibración/temblor visible en bordes de alto contraste.
- **Solución implementada:** Un generador matemático desarrollado en Python que calcula matrices afines de transformación en punto flotante continuo y utiliza remuestreo bicúbico (`Image.Resampling.BICUBIC`) fotograma a fotograma, transmitiendo el flujo en bruto directamente a FFmpeg por tubería (`stdin`). **Resultado: 100% libre de vibración y con fluidez cinematográfica.**

### 2. 🎛️ Estudio Web Interactivo (FastAPI + Vue 3 + Tailwind CSS)
- **Previsualización escena por escena:** Navegación por las 32 escenas del documental con sus textos, duraciones y miniaturas.
- **Búsqueda en Wikimedia Commons:** Buscador integrado que consulta la API de Wikimedia Commons y permite previsualizar y descargar imágenes de alta resolución directamente a la escena activa.
- **Gestión de candidatos:** Carga de imágenes locales con auto-recorte inteligente a 1080p y botón de descarte rápido (papelera 🗑️).
- **Selector de locutor neuronal multivoz:** Panel para probar 6 voces neuronales (`edge-tts`) con preescucha de muestras y regeneración con un clic de todo el audio del proyecto.
- **Banda sonora dinámica (BGM):** Menú para alternar entre diferentes pistas musicales o subir un archivo MP3 propio.
- **Renderizado en segundo plano:** Monitor en vivo con barra de progreso, estado por escena y reproducción directa del video final en el navegador.

### 3. 🎙️ Cadena de Masterización de Audio y Foleys (SFX)
- **Filtro vocal de estudio:**
  ```text
  highpass=f=75, equalizer=f=180:g=3.5, equalizer=f=3200:g=2.2, acompressor=threshold=-18dB:ratio=3.5, alimiter=limit=-1dB
  ```
  Produce una voz de locutor profunda, cálida y limpia de frecuencias parásitas.
- **12 Efectos de sonido (SFX):** Sincronización milimétrica con adelanto y mezcla de volumen para ruidos de sonar abisal, rugidos de reingreso espacial, estática de radio de la ISS, crujidos de hielo en la Antártida y oleaje.
- **11 Tarjetas infográficas animadas (Lower Thirds):** Superposiciones gráficas con transiciones automáticas de entrada y salida (`fade in / fade out`) en momentos clave de datos técnicos.

---

## 📂 Estructura del Proyecto

```text
├── .gitignore
├── requirements.txt
├── README.md
│
└── video_punto_nemo/
    ├── studio/
    │   ├── studio_server.py        # API FastAPI y servidor web del estudio
    │   ├── project_state.json      # Estado persistente del proyecto y escenas
    │   └── templates/
    │       └── index.html          # Interfaz SPA (Vue 3 + Tailwind + FontAwesome)
    │
    ├── subpixel_motion.py          # Motor matemático de paneo/zoom subpíxel
    ├── render_monetizable_8min.py  # Script maestro de compilación de 32 escenas
    ├── build_cinematic_30s_proof.py# Generador de muestras cinematográficas de 30s
    │
    ├── optimized_1080p/            # Fotografías optimizadas a 1920x1080
    ├── overlays/                   # Gráficos PNG de tarjetas informativas (Lower Thirds)
    ├── sfx/                        # Efectos sonoros (WAV/OGG) de alta fidelidad
    ├── media/                      # Videos y metrajes de apoyo (B-roll)
    └── INICIAR_ESTUDIO.bat         # Acceso directo para lanzar el estudio en Windows
```

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/<tu-usuario>/<tu-repositorio>.git
cd <tu-repositorio>
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

> **Nota:** La librería `imageio-ffmpeg` descarga automáticamente el binario ejecutable de FFmpeg correspondiente a tu sistema operativo, sin necesidad de configuraciones manuales en el `PATH`.

### 3. Iniciar el Estudio Web
```bash
cd video_punto_nemo/studio
python studio_server.py
```
O en Windows simplemente haz doble clic en `INICIAR_ESTUDIO.bat`.

Abre tu navegador en:
```text
http://127.0.0.1:8080
```

### 4. Renderizar desde la consola (opcional)
Si prefieres renderizar directamente sin la interfaz:
```bash
cd video_punto_nemo
python render_monetizable_8min.py
```

---

## 🛠️ Modos de Movimiento de Cámara Soportados

En `subpixel_motion.py` se implementan los siguientes movimientos cinematográficos:
- `zoom_in`: Acercamiento lento y constante al centro o sujeto.
- `zoom_out`: Alejamiento progresivo revelador de contexto.
- `pan_right`: Desplazamiento horizontal fluido de izquierda a derecha.
- `pan_left`: Desplazamiento horizontal fluido de derecha a izquierda.
- `drift_up_right`: Paneo diagonal ascendente con suave aumento de escala.
- `drift_down_left`: Paneo diagonal descendente con suave reducción de escala.

---

## 📈 Roadmap de Mejoras Futuras

- [ ] **Generación de subtítulos automáticos:** Integración con `faster-whisper` para generar subtítulos animados palabra por palabra estilo karaoke / MrBeast.
- [ ] **Formato Vertical (9:16):** Exportador directo para YouTube Shorts, Instagram Reels y TikTok.
- [ ] **Transiciones dinámicas:** Disolvencias cruzadas (`crossfade`) y cortinillas cinemáticas entre escenas.
- [ ] **Soporte de Inteligencia Artificial para Guiones:** Asistente generador de guiones y distribución de tiempos automática por temática.

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
