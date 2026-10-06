import os
import json

folder = os.path.expanduser('~/Downloads/fruta-editor')
json_path = os.path.join(folder, 'clips_timeline_data.json')
with open(json_path, 'r', encoding='utf-8') as f:
    project_data = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="es" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FrutiNovela Studio • CapCut Video Editor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              teal: '#00f2fe',
              blue: '#4facfe',
              purple: '#8b5cf6',
              rose: '#f43f5e',
              amber: '#f59e0b',
              dark: '#0e0e12',
              card: '#18181f',
              border: '#2a2a36'
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      height: 8px;
      width: 8px;
    }
    ::-webkit-scrollbar-track {
      background: #121217;
    }
    ::-webkit-scrollbar-thumb {
      background: #2a2a38;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #3f3f52;
    }

    /* Striped pattern for cut silences */
    .bg-striped-cut {
      background: repeating-linear-gradient(
        -45deg,
        rgba(239, 68, 68, 0.45),
        rgba(239, 68, 68, 0.45) 6px,
        rgba(239, 68, 68, 0.15) 6px,
        rgba(239, 68, 68, 0.15) 12px
      );
      border: 1px dashed rgba(239, 68, 68, 0.8);
    }

    /* Playhead styling */
    #playhead {
      pointer-events: none;
      transition: left 0.04s linear;
    }
    .playhead-handle {
      pointer-events: auto;
      cursor: ew-resize;
    }

    /* Pulse animation for active rendering */
    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 15px rgba(6, 182, 212, 0.4); }
      50% { box-shadow: 0 0 25px rgba(6, 182, 212, 0.8); }
    }
    .render-active {
      animation: pulseGlow 1.5s infinite;
    }
  </style>
</head>
<body class="bg-[#0b0b0e] text-zinc-100 min-h-screen flex flex-col font-sans select-none antialiased">

  <!-- TOP HEADER / STUDIO NAVBAR -->
  <header class="h-14 border-b border-[#23232e] bg-[#121217] px-4 flex items-center justify-between shrink-0">
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <span class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-blue-600 flex items-center justify-center text-sm font-black text-black shadow-lg shadow-cyan-500/20">
          🎬
        </span>
        <div>
          <h1 class="text-sm font-bold tracking-wide uppercase text-zinc-100 flex items-center gap-2">
            CapCut FrutiNovela <span class="text-cyan-400 font-semibold">Video Studio</span>
          </h1>
          <div class="flex items-center gap-2 text-[10px] text-zinc-400 font-mono">
            <span>Capítulo 2: Herencia de Sangre (15 Escenas)</span>
            <span class="text-zinc-600">•</span>
            <span class="text-emerald-400">9:16 Vertical Nativo</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Center Status / Duration Info -->
    <div class="hidden lg:flex items-center gap-4 bg-[#181822] px-3 py-1 rounded-lg border border-[#2b2b3a] text-xs">
      <div class="flex items-center gap-2">
        <span class="text-zinc-400">Duración Final:</span>
        <span id="headerTotalDuration" class="font-mono font-bold text-cyan-300">01:36.1s</span>
      </div>
      <div class="h-3 w-px bg-zinc-700"></div>
      <div class="flex items-center gap-2">
        <span class="text-zinc-400">Silencios Ahorrados:</span>
        <span id="headerTotalSavings" class="font-mono font-bold text-rose-400">4.14s</span>
      </div>
      <div class="h-3 w-px bg-zinc-700"></div>
      <div class="flex items-center gap-2">
        <span class="text-zinc-400">Estado:</span>
        <span id="headerRenderStatus" class="font-mono text-emerald-400 font-medium flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Listo para Exportar
        </span>
      </div>
    </div>

    <!-- Right Actions -->
    <div class="flex items-center gap-2 text-xs">
      <button onclick="toggleModal('ecosystemModal')" class="px-2.5 py-1.5 rounded-lg bg-[#1f1f2b] hover:bg-[#282838] border border-[#303042] text-zinc-300 transition flex items-center gap-1.5">
        <span>🔗</span> Antigravity Studio Info
      </button>

      <button onclick="openAutoSilenceModal()" class="px-2.5 py-1.5 rounded-lg bg-[#1f1f2b] hover:bg-[#282838] border border-[#303042] text-amber-300 transition flex items-center gap-1.5">
        <span>⚡</span> Calibrar Silencios (dB)
      </button>

      <!-- BIG RENDER / EXPORT BUTTON -->
      <button id="btnRenderMaster" onclick="triggerRenderVideo()" class="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-600 hover:from-cyan-300 hover:to-indigo-500 text-black font-bold shadow-lg shadow-cyan-500/25 transition flex items-center gap-2 cursor-pointer">
        <span id="renderBtnIcon">🚀</span>
        <span id="renderBtnText">Renderizar Cambios</span>
      </button>
    </div>
  </header>

  <!-- MAIN WORKSPACE -->
  <main class="flex-1 flex flex-col min-h-0">
    
    <!-- UPPER HALF: PLAYER & INSPECTOR WITH EDITING CONTROLS -->
    <section class="h-[440px] p-3 flex gap-3 shrink-0 bg-[#0f0f14] border-b border-[#23232e]">
      
      <!-- LEFT: VIDEO MONITOR (9:16 VERTICAL CAPCUT STYLE) -->
      <div class="w-[330px] bg-[#15151c] rounded-xl border border-[#262634] flex flex-col items-center justify-between p-3 relative shadow-xl shrink-0">
        
        <!-- Video Source Switcher Tabs -->
        <div class="w-full flex items-center justify-between text-xs mb-1.5">
          <div class="flex bg-[#0c0c10] p-0.5 rounded-lg border border-[#23232e]">
            <button id="btnSourceMaster" onclick="switchVideoSource('master')" class="px-2.5 py-1 rounded-md text-[11px] font-semibold bg-cyan-500 text-black shadow transition">
              🎬 Master Editado
            </button>
            <button id="btnSourceRaw" onclick="switchVideoSource('raw')" class="px-2.5 py-1 rounded-md text-[11px] font-medium text-zinc-400 hover:text-zinc-200 transition">
              🎞️ Clip Crudo (kX)
            </button>
          </div>
          <span id="playerSourceTag" class="text-[10px] text-cyan-400 font-mono tracking-tight truncate max-w-[120px]">
            Master
          </span>
        </div>

        <!-- 9:16 Phone/TikTok Frame Container -->
        <div class="relative w-[180px] h-[320px] bg-black rounded-xl overflow-hidden border border-[#303042] shadow-2xl flex items-center justify-center group">
          <video id="mainVideo" class="w-full h-full object-cover" playsinline preload="auto">
            <source id="videoSource" src="CAPITULO_2_FINAL.mp4" type="video/mp4">
            Tu navegador no soporta video MP4.
          </video>

          <!-- Floating Overlay Badges -->
          <div class="absolute top-2 left-2 pointer-events-none flex flex-col gap-1">
            <span id="floatingSceneBadge" class="bg-black/80 backdrop-blur-md border border-white/10 text-[10px] font-mono px-2 py-0.5 rounded text-white shadow">
              Escena 1
            </span>
          </div>

          <!-- Center Click Overlay for Play/Pause -->
          <div id="playCenterOverlay" onclick="togglePlay()" class="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-[1px] opacity-0 group-hover:opacity-100 transition cursor-pointer">
            <div class="w-12 h-12 rounded-full bg-cyan-500/90 text-black flex items-center justify-center text-xl shadow-lg transform group-hover:scale-105 transition">
              ▶
            </div>
          </div>
        </div>

        <!-- Mini Transport Controls Bar -->
        <div class="w-full flex items-center justify-between text-xs mt-2 px-1 text-zinc-400">
          <div class="flex items-center gap-1">
            <button onclick="stepFrame(-1)" title="Retroceder 1 Frame (Coma ,)" class="p-1 hover:text-white transition">⏮</button>
            <button onclick="togglePlay()" id="btnPlayPause" class="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-white font-mono text-xs transition">
              ▶ Play
            </button>
            <button onclick="stepFrame(1)" title="Avanzar 1 Frame (Punto .)" class="p-1 hover:text-white transition">⏭</button>
            <button onclick="seekRelative(-3)" title="-3 seg" class="text-[11px] px-1 hover:text-white font-mono">-3s</button>
            <button onclick="seekRelative(3)" title="+3 seg" class="text-[11px] px-1 hover:text-white font-mono">+3s</button>
          </div>
          <div class="flex items-center gap-1.5 font-mono text-[11px]">
            <span id="timecodeCurrent" class="text-cyan-400 font-bold">00:00.0</span>
            <span class="text-zinc-600">/</span>
            <span id="timecodeTotal" class="text-zinc-400">01:36.1</span>
          </div>
        </div>
      </div>

      <!-- RIGHT: INSPECTOR & REAL-TIME EDITING CONTROLS (CAPCUT STYLE) -->
      <div class="flex-1 bg-[#15151c] rounded-xl border border-[#262634] p-3.5 flex flex-col justify-between overflow-y-auto shadow-xl">
        
        <!-- Scene Title & Character Header -->
        <div class="flex items-start justify-between pb-2.5 border-b border-[#232330]">
          <div class="flex items-center gap-3">
            <img id="inspThumb" src="thumbs/k1.jpg" alt="Miniatura" class="w-14 h-20 rounded-lg object-cover border border-[#38384d] shadow-md shrink-0">
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <span id="inspSceneNum" class="text-xs px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 font-bold font-mono">
                  ESCENA 1 / 15
                </span>
                <span id="inspCharBadge" class="text-xs px-2 py-0.5 rounded font-bold" style="background-color: #f9731622; color: #f97316; border: 1px solid #f9731666;">
                  Bruno (Toronja)
                </span>
                <span id="inspTag" class="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 font-mono uppercase">
                  HOOK
                </span>
              </div>
              <h2 id="inspTitle" class="text-base font-bold text-zinc-100 mt-0.5">
                El Pánico de Bruno
              </h2>
              <p id="inspFilename" class="text-xs text-zinc-400 font-mono">
                Archivo: k1.mp4 • En Timeline: 00:00.0s - 00:06.0s
              </p>
            </div>
          </div>

          <!-- Scene Quick Navigation -->
          <div class="flex items-center gap-1.5">
            <button onclick="selectPrevClip()" class="p-1.5 rounded-lg bg-[#222230] hover:bg-[#2c2c3e] border border-[#343448] text-xs text-zinc-300 transition" title="Escena Anterior">
              ◀ Escena
            </button>
            <button onclick="playCurrentSceneOnly()" class="px-2.5 py-1.5 rounded-lg bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-xs text-cyan-300 font-medium flex items-center gap-1 transition shadow">
              <span>▶</span> Escuchar Escena
            </button>
            <button onclick="selectNextClip()" class="p-1.5 rounded-lg bg-[#222230] hover:bg-[#2c2c3e] border border-[#343448] text-xs text-zinc-300 transition" title="Escena Siguiente">
              Escena ▶
            </button>
          </div>
        </div>

        <!-- Dialogue Box -->
        <div class="my-1.5 p-2 rounded-lg bg-[#0d0d12] border border-[#22222e]">
          <span class="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold block mb-0.5">
            Guion / Diálogo de la Escena:
          </span>
          <p id="inspDialogue" class="text-xs text-zinc-200 italic leading-snug">
            "¡Órale, seguridad! ¡Sáquenme a este güey de mi fiesta antes de que llame a la patrulla y se lo lleven al bote!"
          </p>
        </div>

        <!-- REAL-TIME EDITING CONTROLS FOR THIS CLIP (CAPCUT STYLE TRIM) -->
        <div class="p-3 rounded-lg bg-[#111119] border border-[#2c2c3d]">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
              <span>✂️</span> Editor de Recorte de esta Escena (Trim Manual)
            </span>
            <div class="flex gap-2">
              <button onclick="setTrimFromCurrentTime('start')" class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition" title="Fijar Inicio en el tiempo actual del reproductor (Mark In)">
                📍 Iniciar Aquí
              </button>
              <button onclick="setTrimFromCurrentTime('end')" class="text-[10px] px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition" title="Fijar Final en el tiempo actual del reproductor (Mark Out)">
                📍 Finalizar Aquí
              </button>
              <button onclick="resetClipTrim()" class="text-[10px] px-2 py-0.5 rounded bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 transition">
                Restaurar Original
              </button>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <!-- Start Trim Editor -->
            <div class="bg-[#181822] p-2 rounded-lg border border-[#272738]">
              <div class="flex justify-between items-center mb-1">
                <span class="text-zinc-400 text-[11px]">Silencio Inicial a Cortar:</span>
                <span id="displayStartTrim" class="font-mono font-bold text-rose-400">0.00s</span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="adjustStartTrim(-0.2)" class="px-2 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">-0.2s</button>
                <button onclick="adjustStartTrim(-0.05)" class="px-1.5 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">-0.05</button>
                <input id="inputStartTrim" type="number" step="0.01" min="0" max="4" value="0.00" onchange="onStartTrimInputChange(this.value)" class="w-16 bg-[#0e0e14] border border-[#3b3b50] rounded px-1.5 py-0.5 text-center font-mono text-zinc-100 text-xs">
                <button onclick="adjustStartTrim(0.05)" class="px-1.5 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">+0.05</button>
                <button onclick="adjustStartTrim(0.2)" class="px-2 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">+0.2s</button>
              </div>
            </div>

            <!-- End Trim Editor -->
            <div class="bg-[#181822] p-2 rounded-lg border border-[#272738]">
              <div class="flex justify-between items-center mb-1">
                <span class="text-zinc-400 text-[11px]">Punto de Corte Final:</span>
                <span id="displayEndTrim" class="font-mono font-bold text-emerald-400">6.02s</span>
              </div>
              <div class="flex items-center gap-1.5">
                <button onclick="adjustEndTrim(-0.2)" class="px-2 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">-0.2s</button>
                <button onclick="adjustEndTrim(-0.05)" class="px-1.5 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">-0.05</button>
                <input id="inputEndTrim" type="number" step="0.01" min="1" max="10" value="6.02" onchange="onEndTrimInputChange(this.value)" class="w-16 bg-[#0e0e14] border border-[#3b3b50] rounded px-1.5 py-0.5 text-center font-mono text-zinc-100 text-xs">
                <button onclick="adjustEndTrim(0.05)" class="px-1.5 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">+0.05</button>
                <button onclick="adjustEndTrim(0.2)" class="px-2 py-0.5 rounded bg-[#252536] hover:bg-[#303046] text-zinc-300 font-mono text-[11px]">+0.2s</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Internal Pauses Alert / Diagnostic & One-Click Trim -->
        <div id="internalPausesContainer" class="p-2 rounded-lg bg-[#18151f] border border-[#3b2b4d] flex items-center justify-between text-xs">
          <div class="flex items-center gap-2">
            <span class="text-base">⚠️</span>
            <div>
              <span class="font-bold text-amber-300 text-[11px] block">
                Pausas Intermedias en el Diálogo (Sin Recortar):
              </span>
              <span id="internalPausesText" class="text-[11px] text-zinc-300">
                Ninguna pausa intermedia en este clip.
              </span>
            </div>
          </div>
          <div id="internalPausesButtons" class="flex gap-1.5">
            <!-- Buttons injected by JS -->
          </div>
        </div>

      </div>

    </section>

    <!-- LOWER HALF: MULTI-TRACK CAPCUT TIMELINE -->
    <section class="flex-1 flex flex-col bg-[#0d0d12] relative overflow-hidden">
      
      <!-- Timeline Header Controls Bar -->
      <div class="h-10 border-b border-[#23232e] bg-[#121217] px-4 flex items-center justify-between shrink-0 text-xs">
        
        <!-- Left: Track Tools & Snapping -->
        <div class="flex items-center gap-3">
          <span class="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-cyan-400"></span> Línea de Tiempo Multipista
          </span>
          <div class="h-4 w-px bg-zinc-700"></div>
          <!-- Legend -->
          <div class="flex items-center gap-3 text-[11px] text-zinc-400">
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded bg-cyan-600 inline-block"></span> Video Útil</span>
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded bg-rose-500/50 border border-rose-500 inline-block"></span> ✂️ Silencio Cortado</span>
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded bg-amber-500/60 inline-block"></span> ⚠️ Pausa Intermedia</span>
            <span class="flex items-center gap-1"><span class="w-3 h-2 rounded bg-purple-600 inline-block"></span> 🎵 Música BGM</span>
          </div>
        </div>

        <!-- Right: Zoom & Navigation -->
        <div class="flex items-center gap-2">
          <span class="text-[11px] text-zinc-500">Zoom:</span>
          <button onclick="setZoom(0.7)" class="px-2 py-0.5 rounded bg-[#1e1e26] hover:bg-[#282834] text-zinc-300">70%</button>
          <button onclick="setZoom(1.0)" class="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300 font-bold">100%</button>
          <button onclick="setZoom(1.6)" class="px-2 py-0.5 rounded bg-[#1e1e26] hover:bg-[#282834] text-zinc-300">160%</button>
          <button onclick="fitTimeline()" class="px-2 py-0.5 rounded bg-[#1e1e26] hover:bg-[#282834] text-zinc-300">Ajustar Pantalla</button>
        </div>
      </div>

      <!-- SCROLLABLE TIMELINE CONTAINER -->
      <div id="timelineScrollContainer" class="flex-1 overflow-x-auto overflow-y-hidden relative p-3">
        
        <!-- Timeline Canvas / Layout Area -->
        <div id="timelineTrackArea" class="relative min-w-full h-[260px] pb-4" onclick="handleTimelineClick(event)">
          
          <!-- TIME RULER (Top Ruler with seconds markers) -->
          <div id="timeRuler" class="h-6 border-b border-[#252533] relative mb-1 text-[10px] font-mono text-zinc-500 select-none">
            <!-- Seconds ticks injected by JS -->
          </div>

          <!-- TRACK 1: VIDEO SCENES (15 CLIPS) -->
          <div class="h-16 bg-[#13131b] border border-[#232332] rounded-lg relative mb-2 flex items-center overflow-hidden">
            <div class="absolute left-1 top-1 text-[9px] font-bold text-zinc-500 tracking-wider uppercase z-20 pointer-events-none bg-black/60 px-1 rounded">
              Pista 1: Video (15 Escenas)
            </div>
            <div id="videoClipsTrack" class="w-full h-full relative">
              <!-- Clip Blocks injected by JS -->
            </div>
          </div>

          <!-- TRACK 2: SPEECH WAVEFORM & SILENCE DETECTION -->
          <div class="h-14 bg-[#13131b] border border-[#232332] rounded-lg relative mb-2 flex items-center overflow-hidden">
            <div class="absolute left-1 top-1 text-[9px] font-bold text-emerald-400/80 tracking-wider uppercase z-20 pointer-events-none bg-black/60 px-1 rounded">
              Pista 2: Voz y Detección de Silencios (-28dB)
            </div>
            <div id="waveformTrack" class="w-full h-full relative">
              <!-- Waveform SVG & Silence Marks injected by JS -->
            </div>
          </div>

          <!-- TRACK 3: BACKGROUND MUSIC (music-frutas.mp3) -->
          <div class="h-12 bg-[#13131b] border border-[#232332] rounded-lg relative flex items-center overflow-hidden">
            <div class="absolute left-1 top-1 text-[9px] font-bold text-purple-400 tracking-wider uppercase z-20 pointer-events-none bg-black/60 px-1 rounded">
              Pista 3: Música de Fondo (music-frutas.mp3)
            </div>
            <div id="musicTrack" class="w-full h-full relative">
              <!-- Music Bar & Fade Out injected by JS -->
            </div>
          </div>

          <!-- RED VERTICAL PLAYHEAD LINE -->
          <div id="playhead" class="absolute top-0 bottom-0 w-[2px] bg-rose-500 z-50 pointer-events-none" style="left: 0px;">
            <div class="playhead-handle -translate-x-1/2 -top-1 w-3.5 h-3.5 bg-rose-500 rounded-sm rotate-45 border border-white shadow-lg pointer-events-auto cursor-ew-resize"></div>
            <div id="playheadTimeBubble" class="absolute -top-6 -translate-x-1/2 px-1.5 py-0.5 rounded bg-rose-600 text-[10px] font-mono text-white font-bold whitespace-nowrap shadow-md pointer-events-none">
              00:00.0
            </div>
          </div>

        </div>

      </div>

    </section>

  </main>

  <!-- MODAL: AUTO-SILENCE CALIBRATION (DECIBELS & PADDING) -->
  <div id="silenceModal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#181824] border border-[#2c2c40] rounded-xl max-w-md w-full p-5 text-zinc-200 shadow-2xl">
      <div class="flex items-center justify-between pb-3 border-b border-[#2c2c40]">
        <h3 class="text-sm font-bold text-zinc-100 flex items-center gap-2">
          <span>⚡</span> Calibración de Silencios Automática (FFmpeg)
        </h3>
        <button onclick="toggleModal('silenceModal')" class="text-zinc-400 hover:text-white text-lg font-bold">&times;</button>
      </div>

      <div class="my-4 space-y-4 text-xs">
        <div>
          <label class="block text-zinc-300 font-semibold mb-1">
            Umbral de Volumen de Silencio (dB):
          </label>
          <div class="flex items-center gap-3">
            <input id="rangeThreshold" type="range" min="-38" max="-20" step="1" value="-28" oninput="document.getElementById('valThreshold').innerText = this.value + ' dB'" class="flex-1 accent-cyan-400">
            <span id="valThreshold" class="font-mono font-bold text-cyan-400 w-16 text-right">-28 dB</span>
          </div>
          <span class="text-[10px] text-zinc-500 mt-0.5 block">
            -28dB es ideal para voz clara. -32dB es más estricto (corta más pausas).
          </span>
        </div>

        <div>
          <label class="block text-zinc-300 font-semibold mb-1">
            Margen de Respiración de Entrada (Padding):
          </label>
          <div class="flex items-center gap-3">
            <input id="rangePadding" type="range" min="0.02" max="0.15" step="0.01" value="0.06" oninput="document.getElementById('valPadding').innerText = this.value + ' s'" class="flex-1 accent-cyan-400">
            <span id="valPadding" class="font-mono font-bold text-emerald-400 w-16 text-right">0.06 s</span>
          </div>
          <span class="text-[10px] text-zinc-500 mt-0.5 block">
            Margen antes de la primera palabra para evitar comerse consonantes.
          </span>
        </div>

        <div>
          <label class="block text-zinc-300 font-semibold mb-1">
            Duración Mínima de Silencio:
          </label>
          <select id="selectMinDuration" class="w-full bg-[#101016] border border-[#303044] rounded p-2 text-zinc-200">
            <option value="0.20">0.20 segundos (Corte ultra agresivo / ráfaga)</option>
            <option value="0.25" selected>0.25 segundos (Estándar TikTok dinámico)</option>
            <option value="0.35">0.35 segundos (Conservador / pausas suaves)</option>
          </select>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-2 border-t border-[#2c2c40]">
        <button onclick="toggleModal('silenceModal')" class="px-3 py-1.5 rounded-lg bg-[#222230] text-zinc-300 text-xs hover:bg-[#2c2c3e]">
          Cancelar
        </button>
        <button onclick="applyAutoSilenceDetection()" class="px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs transition">
          ⚡ Re-analizar 15 Clips
        </button>
      </div>
    </div>
  </div>

  <!-- MODAL: RELACIÓN CON ANTIGRAVITY VIDEO STUDIO -->
  <div id="ecosystemModal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#181824] border border-[#2c2c40] rounded-xl max-w-lg w-full p-5 text-zinc-200 shadow-2xl">
      <div class="flex items-center justify-between pb-3 border-b border-[#2c2c40]">
        <h3 class="text-sm font-bold text-zinc-100 flex items-center gap-2">
          <span>🎬</span> Ecosistema Antigravity Video Studio
        </h3>
        <button onclick="toggleModal('ecosystemModal')" class="text-zinc-400 hover:text-white text-lg font-bold">&times;</button>
      </div>

      <div class="my-3 space-y-3 text-xs leading-relaxed">
        <p class="text-zinc-300">
          Tu pregunta: <em>"¿Esto va junto con el otro Antigravity Video Studio o los hiciste separados?"</em>
        </p>

        <div class="p-2.5 rounded-lg bg-[#111118] border border-[#282838]">
          <h4 class="font-bold text-cyan-400 flex items-center gap-1.5 mb-1">
            <span>📺</span> 1. Antigravity Video Studio (YouTube Documentales - 16:9)
          </h4>
          <p class="text-zinc-400 text-[11px]">
            Ubicado en <code>beautiful-hertz</code> (puerto 8080). Diseñado para documentales largos (8+ min) como Punto Nemo y Barcos Modernos: motor de paneo subpíxel anti-temblor, voces neuronales (edge-tts) y efectos SFX.
          </p>
        </div>

        <div class="p-2.5 rounded-lg bg-[#111118] border border-[#282838]">
          <h4 class="font-bold text-rose-400 flex items-center gap-1.5 mb-1">
            <span>📱</span> 2. FrutiNovela Studio (TikTok & Reels - 9:16)
          </h4>
          <p class="text-zinc-400 text-[11px]">
            Ubicado en <code>Downloads/fruta-editor</code> (puerto 8088). Diseñado para videos cortos virales de comedia/drama: ensamble de escenas Veo, corte milimétrico de silencios, y mezcla de música BGM.
          </p>
        </div>

        <p class="text-zinc-300 text-[11px]">
          ✅ <strong>Están separados intencionalmente para máxima velocidad y especialización</strong>, pero comparten el mismo motor de renderizado FFmpeg de Antigravity. Podemos unirlos en una sola suite si prefieres tener una pestaña para documentales y otra para novelas verticales.
        </p>
      </div>

      <div class="pt-2 text-right">
        <button onclick="toggleModal('ecosystemModal')" class="px-4 py-1.5 rounded-lg bg-cyan-500 text-black font-semibold text-xs hover:bg-cyan-400 transition">
          Entendido
        </button>
      </div>
    </div>
  </div>

  <!-- MODAL: RENDERING IN PROGRESS -->
  <div id="renderProgressModal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#171724] border border-cyan-500/50 rounded-2xl max-w-sm w-full p-6 text-center shadow-2xl render-active">
      <div class="w-14 h-14 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-2xl mx-auto mb-3 animate-spin">
        ⚙️
      </div>
      <h3 class="text-base font-bold text-white mb-1">
        Renderizando Video con Nuevos Cortes
      </h3>
      <p id="renderStatusMsg" class="text-xs text-zinc-400 mb-4">
        Ejecutando FFmpeg en segundo plano...
      </p>

      <div class="w-full bg-[#0d0d14] rounded-full h-2.5 border border-[#2b2b40] overflow-hidden mb-2">
        <div id="renderProgressBar" class="bg-gradient-to-r from-cyan-400 to-blue-500 h-full w-2/3 animate-pulse"></div>
      </div>
      <span class="text-[10px] text-zinc-500 font-mono">
        Recortando clips • Concatenando • Mezclando BGM
      </span>
    </div>
  </div>

  <!-- EMBEDDED PROJECT DATA -->
  <script>
    let PROJECT_DATA = """ + json.dumps(project_data, ensure_ascii=False) + """;
  </script>

  <!-- APP CONTROLLER JAVASCRIPT -->
  <script>
    const video = document.getElementById('mainVideo');
    let totalDuration = PROJECT_DATA.total_duration;
    let selectedClipIndex = 1;
    let zoomLevel = 1.0;
    let currentSourceMode = 'master'; // 'master' or 'raw'
    let isDraggingPlayhead = false;

    // Initialize application
    window.addEventListener('DOMContentLoaded', () => {
      recalcTimelinePositions();
      renderTimeRuler();
      renderVideoClipsTrack();
      renderWaveformTrack();
      renderMusicTrack();
      selectClip(1);
      setupVideoListeners();
      setupKeyboardShortcuts();
      setupPlayheadDragger();
      updateHeaderStats();
    });

    function recalcTimelinePositions() {
      let cur = 0.0;
      PROJECT_DATA.clips.forEach(clip => {
        clip.timeline_start = round3(cur);
        clip.trimmed_duration = round3(clip.end_trim - clip.start_trim);
        clip.timeline_end = round3(cur + clip.trimmed_duration);
        cur += clip.trimmed_duration;
      });
      totalDuration = round3(cur);
      PROJECT_DATA.total_duration = totalDuration;
    }

    function round3(val) {
      return Math.round(val * 1000) / 1000;
    }

    function getBasePixelsPerSecond() {
      const containerWidth = document.getElementById('timelineScrollContainer').clientWidth - 30;
      const base = Math.max(containerWidth / totalDuration, 12);
      return base * zoomLevel;
    }

    function timeToPixels(seconds) {
      return seconds * getBasePixelsPerSecond();
    }

    function pixelsToTime(px) {
      return Math.max(0, Math.min(totalDuration, px / getBasePixelsPerSecond()));
    }

    function setZoom(level) {
      zoomLevel = level;
      refreshTimelineLayout();
    }

    function fitTimeline() {
      const containerWidth = document.getElementById('timelineScrollContainer').clientWidth - 40;
      zoomLevel = containerWidth / (totalDuration * 12);
      refreshTimelineLayout();
    }

    function refreshTimelineLayout() {
      recalcTimelinePositions();
      const pxPerSec = getBasePixelsPerSecond();
      const totalWidth = totalDuration * pxPerSec;
      document.getElementById('timelineTrackArea').style.width = totalWidth + 'px';

      renderTimeRuler();
      renderVideoClipsTrack();
      renderWaveformTrack();
      renderMusicTrack();
      updatePlayheadPosition(video.currentTime);
      updateHeaderStats();
    }

    function updateHeaderStats() {
      document.getElementById('headerTotalDuration').innerText = formatTimecode(totalDuration);
      let totalSaved = 0.0;
      PROJECT_DATA.clips.forEach(c => {
        totalSaved += (c.total_duration - c.trimmed_duration);
      });
      document.getElementById('headerTotalSavings').innerText = `${totalSaved.toFixed(2)}s`;
    }

    // Render Seconds Ticks in Ruler
    function renderTimeRuler() {
      const ruler = document.getElementById('timeRuler');
      ruler.innerHTML = '';
      const pxPerSec = getBasePixelsPerSecond();
      const step = zoomLevel > 1.3 ? 2 : (zoomLevel < 0.8 ? 10 : 5);

      for (let sec = 0; sec <= totalDuration; sec += step) {
        const left = sec * pxPerSec;
        const tick = document.createElement('div');
        tick.className = 'absolute top-0 bottom-0 border-l border-[#2e2e3f] pl-1';
        tick.style.left = left + 'px';
        
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        tick.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        ruler.appendChild(tick);
      }
    }

    // Render Video Scenes Track
    function renderVideoClipsTrack() {
      const track = document.getElementById('videoClipsTrack');
      track.innerHTML = '';
      const pxPerSec = getBasePixelsPerSecond();

      PROJECT_DATA.clips.forEach(clip => {
        const startPx = clip.timeline_start * pxPerSec;
        const widthPx = clip.trimmed_duration * pxPerSec;

        const block = document.createElement('div');
        block.id = `clip-block-${clip.index}`;
        block.className = `absolute top-1 bottom-1 rounded-md border flex items-center justify-between px-2 cursor-pointer transition-all duration-150 overflow-hidden ${
          clip.index === selectedClipIndex 
            ? 'bg-[#1e293b] border-cyan-400 shadow-md ring-1 ring-cyan-400' 
            : 'bg-[#141d2b] border-[#22334d] hover:border-cyan-500/60'
        }`;
        block.style.left = startPx + 'px';
        block.style.width = Math.max(widthPx, 24) + 'px';
        block.onclick = (e) => {
          e.stopPropagation();
          selectClip(clip.index);
          seekTo(clip.timeline_start);
        };

        // Thumbnail + label
        block.innerHTML = `
          <div class="flex items-center gap-1.5 pointer-events-none truncate z-10">
            <img src="thumbs/${clip.filename.replace('.mp4', '.jpg')}" class="w-6 h-9 rounded object-cover border border-white/20 shrink-0">
            <div class="truncate">
              <span class="text-[10px] font-bold text-cyan-300 font-mono">k${clip.index}</span>
              <span class="text-[10px] text-zinc-300 truncate hidden sm:inline ml-1">${clip.char.split(' ')[0]}</span>
            </div>
          </div>
          <span class="text-[9px] font-mono text-zinc-400 pointer-events-none shrink-0 z-10">${clip.trimmed_duration.toFixed(1)}s</span>
        `;

        // Visual Cut Indicators
        if (clip.start_trim > 0.05) {
          const cutStart = document.createElement('div');
          cutStart.className = 'absolute top-0 bottom-0 left-0 bg-striped-cut z-0 flex items-center justify-center';
          cutStart.style.width = Math.max(14, clip.start_trim * pxPerSec * 0.7) + 'px';
          cutStart.title = `Silencio inicial cortado: ${clip.start_trim}s`;
          cutStart.innerHTML = '<span class="text-[8px]">✂️</span>';
          block.appendChild(cutStart);
        }

        const endCutAmount = clip.total_duration - clip.end_trim;
        if (endCutAmount > 0.05) {
          const cutEnd = document.createElement('div');
          cutEnd.className = 'absolute top-0 bottom-0 right-0 bg-striped-cut z-0 flex items-center justify-center';
          cutEnd.style.width = Math.max(14, endCutAmount * pxPerSec * 0.7) + 'px';
          cutEnd.title = `Silencio final cortado: ${endCutAmount.toFixed(2)}s`;
          cutEnd.innerHTML = '<span class="text-[8px]">✂️</span>';
          block.appendChild(cutEnd);
        }

        track.appendChild(block);
      });
    }

    // Render Waveform and Silence Marks Track
    function renderWaveformTrack() {
      const track = document.getElementById('waveformTrack');
      track.innerHTML = '';
      const pxPerSec = getBasePixelsPerSecond();

      PROJECT_DATA.clips.forEach(clip => {
        const startPx = clip.timeline_start * pxPerSec;
        const widthPx = clip.trimmed_duration * pxPerSec;

        const waveBox = document.createElement('div');
        waveBox.className = 'absolute top-0 bottom-0 flex items-center border-r border-[#1a1a24]';
        waveBox.style.left = startPx + 'px';
        waveBox.style.width = widthPx + 'px';

        // Draw waveform bars
        const peaks = clip.waveform || [];
        const barsCount = Math.max(10, Math.floor(widthPx / 4));
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("class", "w-full h-full");
        svg.setAttribute("viewBox", `0 0 ${barsCount} 100`);
        svg.setAttribute("preserveAspectRatio", "none");

        let svgContent = '';
        for (let i = 0; i < barsCount; i++) {
          const peakIdx = Math.floor((i / barsCount) * peaks.length);
          const amp = (peaks[peakIdx] || 0.3) * 75;
          const y = (100 - amp) / 2;
          svgContent += `<rect x="${i}" y="${y}" width="0.75" height="${amp}" fill="#10b981" rx="0.3" opacity="0.85"/>`;
        }
        svg.innerHTML = svgContent;
        waveBox.appendChild(svg);

        // Highlight Internal Pauses
        if (clip.internal_pauses && clip.internal_pauses.length > 0) {
          clip.internal_pauses.forEach(pause => {
            const pauseLeftPx = (pause.timeline_pos - clip.timeline_start) * pxPerSec;
            const pauseWidthPx = Math.max(18, pause.duration * pxPerSec);

            const pauseBadge = document.createElement('div');
            pauseBadge.className = 'absolute top-1 bottom-1 bg-amber-500/70 border border-amber-300 rounded flex items-center justify-center text-[9px] font-bold text-black cursor-pointer hover:bg-amber-400 shadow-md z-10';
            pauseBadge.style.left = pauseLeftPx + 'px';
            pauseBadge.style.width = pauseWidthPx + 'px';
            pauseBadge.title = `Pausa interna en diálogo: ${pause.duration}s. Clic para escuchar`;
            pauseBadge.innerHTML = `⚠️ ${pause.duration}s`;
            pauseBadge.onclick = (e) => {
              e.stopPropagation();
              selectClip(clip.index);
              seekTo(pause.timeline_pos);
            };
            waveBox.appendChild(pauseBadge);
          });
        }

        track.appendChild(waveBox);
      });
    }

    // Render Music Track
    function renderMusicTrack() {
      const track = document.getElementById('musicTrack');
      track.innerHTML = '';
      const pxPerSec = getBasePixelsPerSecond();
      const totalWidth = totalDuration * pxPerSec;

      const musicBar = document.createElement('div');
      musicBar.className = 'absolute top-1 bottom-1 left-0 rounded-md bg-gradient-to-r from-purple-900/80 via-purple-700/80 to-purple-600/40 border border-purple-500/60 flex items-center justify-between px-3 text-xs text-purple-200';
      musicBar.style.width = totalWidth + 'px';

      musicBar.innerHTML = `
        <div class="flex items-center gap-2 pointer-events-none">
          <span>🎵</span>
          <span class="font-mono text-[11px] font-medium">music-frutas.mp3 (Volumen 100%)</span>
        </div>
        <div class="flex items-center gap-1 bg-black/40 px-2 py-0.5 rounded border border-purple-400/40 text-[10px] font-mono text-purple-300">
          <span>📉 Fade Out Final (2.5s)</span>
        </div>
      `;

      track.appendChild(musicBar);
    }

    // Select and inspect a specific clip
    function selectClip(index) {
      selectedClipIndex = index;
      const clip = PROJECT_DATA.clips.find(c => c.index === index) || PROJECT_DATA.clips[0];

      // Update Inspector Elements
      document.getElementById('inspThumb').src = `thumbs/${clip.filename.replace('.mp4', '.jpg')}`;
      document.getElementById('inspSceneNum').innerText = `ESCENA ${clip.index} / 15`;
      document.getElementById('inspTitle').innerText = clip.title;
      document.getElementById('inspFilename').innerText = `Archivo: ${clip.filename} • En Timeline: ${formatTimecode(clip.timeline_start)} - ${formatTimecode(clip.timeline_end)}`;
      document.getElementById('inspDialogue').innerText = `"${clip.dialogue}"`;

      // Character Badge
      const charBadge = document.getElementById('inspCharBadge');
      charBadge.innerText = clip.char;
      charBadge.style.backgroundColor = `${clip.color}22`;
      charBadge.style.color = clip.color;
      charBadge.style.borderColor = `${clip.color}66`;

      document.getElementById('inspTag').innerText = clip.tag;

      // Update Trimming Inputs
      document.getElementById('displayStartTrim').innerText = `${clip.start_trim.toFixed(2)}s`;
      document.getElementById('inputStartTrim').value = clip.start_trim.toFixed(2);

      document.getElementById('displayEndTrim').innerText = `${clip.end_trim.toFixed(2)}s`;
      document.getElementById('inputEndTrim').value = clip.end_trim.toFixed(2);
      document.getElementById('inputEndTrim').max = clip.total_duration;

      // Internal pauses
      const pausesBox = document.getElementById('internalPausesText');
      const pauseButtons = document.getElementById('internalPausesButtons');
      pauseButtons.innerHTML = '';

      if (clip.internal_pauses && clip.internal_pauses.length > 0) {
        pausesBox.innerHTML = `<span class="text-amber-400 font-semibold">${clip.internal_pauses.length} pausa(s) detectada(s)</span> en medio de las frases de este personaje.`;
        clip.internal_pauses.forEach((p, idx) => {
          const btn = document.createElement('button');
          btn.className = 'px-2 py-1 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-[10px] transition shadow';
          btn.innerText = `Escuchar Pausa #${idx+1} (${p.duration}s)`;
          btn.onclick = () => {
            seekTo(p.timeline_pos);
            video.play();
          };
          pauseButtons.appendChild(btn);
        });
      } else {
        pausesBox.innerText = 'El diálogo en este clip es continuo y fluido (no hay silencios intermedios significativos).';
      }

      // If in raw mode, update raw video source
      if (currentSourceMode === 'raw') {
        video.src = clip.filename;
        video.currentTime = 0;
        document.getElementById('playerSourceTag').innerText = clip.filename;
      }

      // Highlight in timeline
      PROJECT_DATA.clips.forEach(c => {
        const el = document.getElementById(`clip-block-${c.index}`);
        if (el) {
          if (c.index === index) {
            el.className = el.className.replace('bg-[#141d2b]', 'bg-[#1e293b]').replace('border-[#22334d]', 'border-cyan-400 ring-1 ring-cyan-400');
          } else {
            el.className = el.className.replace('bg-[#1e293b]', 'bg-[#141d2b]').replace('border-cyan-400 ring-1 ring-cyan-400', 'border-[#22334d]');
          }
        }
      });
    }

    function selectPrevClip() {
      const prev = Math.max(1, selectedClipIndex - 1);
      selectClip(prev);
      const clip = PROJECT_DATA.clips.find(c => c.index === prev);
      if (clip) seekTo(clip.timeline_start);
    }

    function selectNextClip() {
      const next = Math.min(PROJECT_DATA.clips.length, selectedClipIndex + 1);
      selectClip(next);
      const clip = PROJECT_DATA.clips.find(c => c.index === next);
      if (clip) seekTo(clip.timeline_start);
    }

    // EDITING: Adjust Start Trim
    function adjustStartTrim(delta) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      const newVal = Math.max(0.0, Math.min(clip.end_trim - 0.5, round3(clip.start_trim + delta)));
      clip.start_trim = newVal;
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    function onStartTrimInputChange(val) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      const num = parseFloat(val);
      if (isNaN(num)) return;
      clip.start_trim = Math.max(0.0, Math.min(clip.end_trim - 0.5, round3(num)));
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    // EDITING: Adjust End Trim
    function adjustEndTrim(delta) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      const newVal = Math.max(clip.start_trim + 0.5, Math.min(clip.total_duration, round3(clip.end_trim + delta)));
      clip.end_trim = newVal;
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    function onEndTrimInputChange(val) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      const num = parseFloat(val);
      if (isNaN(num)) return;
      clip.end_trim = Math.max(clip.start_trim + 0.5, Math.min(clip.total_duration, round3(num)));
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    // Mark In / Mark Out from player position
    function setTrimFromCurrentTime(type) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      const cur = video.currentTime;
      let clipTime = cur;
      if (currentSourceMode === 'master') {
        clipTime = (cur - clip.timeline_start) + clip.start_trim;
      }
      clipTime = Math.max(0.0, Math.min(clip.total_duration, round3(clipTime)));

      if (type === 'start') {
        if (clipTime < clip.end_trim - 0.3) {
          clip.start_trim = clipTime;
        }
      } else {
        if (clipTime > clip.start_trim + 0.3) {
          clip.end_trim = clipTime;
        }
      }
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    function resetClipTrim() {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      clip.start_trim = 0.0;
      clip.end_trim = clip.total_duration;
      selectClip(selectedClipIndex);
      refreshTimelineLayout();
      markUnsavedChanges();
    }

    function markUnsavedChanges() {
      document.getElementById('headerRenderStatus').innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span> Cambios Pendientes de Render';
      document.getElementById('headerRenderStatus').className = 'font-mono text-amber-400 font-medium flex items-center gap-1';
      document.getElementById('btnRenderMaster').classList.add('render-active');
    }

    // API: TRIGGER RENDER MASTER VIDEO
    async function triggerRenderVideo() {
      const modal = document.getElementById('renderProgressModal');
      modal.classList.remove('hidden');
      document.getElementById('renderStatusMsg').innerText = 'Recortando y ensamblando 15 escenas con FFmpeg...';

      try {
        const payload = {
          clips: PROJECT_DATA.clips.map(c => ({
            filename: c.filename,
            start_trim: c.start_trim,
            end_trim: c.end_trim
          })),
          music_file: 'music-frutas.mp3',
          music_volume: 1.0,
          fade_out: 2.5
        };

        const res = await fetch('/api/render', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.ok) {
          document.getElementById('renderStatusMsg').innerText = `✅ ¡Éxito! Nueva duración: ${data.total_duration}s. Recargando reproductor...`;
          setTimeout(() => {
            modal.classList.add('hidden');
            // Force reload video with cache-busting
            const bust = Date.now();
            video.src = `CAPITULO_2_FINAL.mp4?v=${bust}`;
            video.load();
            video.play().catch(() => {});

            document.getElementById('headerRenderStatus').innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400"></span> Master Actualizado ✅';
            document.getElementById('headerRenderStatus').className = 'font-mono text-emerald-400 font-medium flex items-center gap-1';
            document.getElementById('btnRenderMaster').classList.remove('render-active');
          }, 1200);
        } else {
          alert('Error al renderizar: ' + (data.error || 'Desconocido'));
          modal.classList.add('hidden');
        }
      } catch (err) {
        alert('Error conectando con el servidor local: ' + err.message);
        modal.classList.add('hidden');
      }
    }

    // API: AUTO-SILENCE DETECTION
    function openAutoSilenceModal() {
      toggleModal('silenceModal');
    }

    async function applyAutoSilenceDetection() {
      const threshold = parseInt(document.getElementById('rangeThreshold').value);
      const padding = parseFloat(document.getElementById('rangePadding').value);
      const minDur = parseFloat(document.getElementById('selectMinDuration').value);

      toggleModal('silenceModal');
      const progressModal = document.getElementById('renderProgressModal');
      progressModal.classList.remove('hidden');
      document.getElementById('renderStatusMsg').innerText = `Analizando audio a ${threshold}dB con FFmpeg silencedetect...`;

      try {
        const res = await fetch('/api/detect_silence', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            threshold_db: threshold,
            min_duration: minDur,
            lead_padding: padding,
            trail_padding: padding + 0.05
          })
        });

        const json = await res.json();
        if (json.ok) {
          PROJECT_DATA = json.data;
          refreshTimelineLayout();
          selectClip(selectedClipIndex);
          progressModal.classList.add('hidden');
          markUnsavedChanges();
          alert(`¡Silencios re-analizados a ${threshold}dB! Revisa los cortes y haz clic en 'Renderizar Cambios' para generar el nuevo video.`);
        } else {
          alert('Error: ' + json.error);
          progressModal.classList.add('hidden');
        }
      } catch (e) {
        alert('Error: ' + e.message);
        progressModal.classList.add('hidden');
      }
    }

    function switchVideoSource(mode) {
      currentSourceMode = mode;
      const btnMaster = document.getElementById('btnSourceMaster');
      const btnRaw = document.getElementById('btnSourceRaw');
      const tag = document.getElementById('playerSourceTag');

      if (mode === 'master') {
        btnMaster.className = 'px-2.5 py-1 rounded-md text-[11px] font-semibold bg-cyan-500 text-black shadow transition';
        btnRaw.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-zinc-400 hover:text-zinc-200 transition';
        video.src = 'CAPITULO_2_FINAL.mp4';
        tag.innerText = 'CAPITULO_2_FINAL.mp4';
      } else {
        btnRaw.className = 'px-2.5 py-1 rounded-md text-[11px] font-semibold bg-cyan-500 text-black shadow transition';
        btnMaster.className = 'px-2.5 py-1 rounded-md text-[11px] font-medium text-zinc-400 hover:text-zinc-200 transition';
        const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex) || PROJECT_DATA.clips[0];
        video.src = clip.filename;
        tag.innerText = clip.filename;
      }
      video.play().catch(() => {});
    }

    function playCurrentSceneOnly() {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return;
      seekTo(clip.timeline_start);
      video.play();
    }

    // Video Playback Listeners
    function setupVideoListeners() {
      video.addEventListener('timeupdate', () => {
        if (isDraggingPlayhead) return;
        const cur = currentSourceMode === 'master' ? video.currentTime : getTimelineTimeForRawClip(video.currentTime);
        updatePlayheadPosition(cur);
        updateTimecodeReadout(cur);
        updateActiveSceneFromTime(cur);
      });

      video.addEventListener('play', () => {
        document.getElementById('btnPlayPause').innerText = '⏸ Pausa';
        document.getElementById('playCenterOverlay').style.opacity = '0';
      });

      video.addEventListener('pause', () => {
        document.getElementById('btnPlayPause').innerText = '▶ Play';
        document.getElementById('playCenterOverlay').style.opacity = '1';
      });
    }

    function getTimelineTimeForRawClip(rawSec) {
      const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
      if (!clip) return rawSec;
      return clip.timeline_start + Math.max(0, rawSec - clip.start_trim);
    }

    function updatePlayheadPosition(seconds) {
      const px = timeToPixels(seconds);
      const playhead = document.getElementById('playhead');
      playhead.style.left = px + 'px';
      document.getElementById('playheadTimeBubble').innerText = formatTimecode(seconds);
    }

    function updateTimecodeReadout(seconds) {
      document.getElementById('timecodeCurrent').innerText = formatTimecode(seconds);
    }

    function updateActiveSceneFromTime(seconds) {
      const activeClip = PROJECT_DATA.clips.find(c => seconds >= c.timeline_start && seconds < c.timeline_end);
      if (activeClip && activeClip.index !== selectedClipIndex) {
        selectClip(activeClip.index);
        document.getElementById('floatingSceneBadge').innerText = `Escena ${activeClip.index} (${activeClip.char.split(' ')[0]})`;
      }
    }

    function formatTimecode(sec) {
      if (isNaN(sec)) return "00:00.0";
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      const ms = Math.floor((sec % 1) * 10);
      return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}.${ms}`;
    }

    function togglePlay() {
      if (video.paused) {
        video.play();
      } else {
        video.pause();
      }
    }

    function seekTo(seconds) {
      if (currentSourceMode === 'master') {
        video.currentTime = Math.max(0, Math.min(totalDuration, seconds));
      } else {
        const clip = PROJECT_DATA.clips.find(c => c.index === selectedClipIndex);
        if (clip) {
          const rawSec = (seconds - clip.timeline_start) + clip.start_trim;
          video.currentTime = Math.max(0, Math.min(clip.total_duration, rawSec));
        }
      }
      updatePlayheadPosition(seconds);
      updateTimecodeReadout(seconds);
    }

    function seekRelative(deltaSec) {
      seekTo(video.currentTime + deltaSec);
    }

    function stepFrame(frames) {
      video.pause();
      const delta = frames * (1 / 24);
      seekTo(video.currentTime + delta);
    }

    // Interactive timeline click and drag
    function handleTimelineClick(event) {
      const rect = document.getElementById('timelineTrackArea').getBoundingClientRect();
      const clickX = event.clientX - rect.left;
      const targetTime = pixelsToTime(clickX);
      seekTo(targetTime);
    }

    function setupPlayheadDragger() {
      const handle = document.querySelector('.playhead-handle');
      const trackArea = document.getElementById('timelineTrackArea');

      const onMouseMove = (e) => {
        if (!isDraggingPlayhead) return;
        const rect = trackArea.getBoundingClientRect();
        const curX = e.clientX - rect.left;
        const targetTime = pixelsToTime(curX);
        updatePlayheadPosition(targetTime);
        updateTimecodeReadout(targetTime);
      };

      const onMouseUp = (e) => {
        if (!isDraggingPlayhead) return;
        isDraggingPlayhead = false;
        const rect = trackArea.getBoundingClientRect();
        const curX = e.clientX - rect.left;
        seekTo(pixelsToTime(curX));
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
      };

      handle.addEventListener('mousedown', (e) => {
        e.stopPropagation();
        isDraggingPlayhead = true;
        video.pause();
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      });
    }

    function setupKeyboardShortcuts() {
      window.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.code === 'Space') {
          e.preventDefault();
          togglePlay();
        } else if (e.code === 'ArrowLeft') {
          e.preventDefault();
          seekRelative(-3);
        } else if (e.code === 'ArrowRight') {
          e.preventDefault();
          seekRelative(3);
        } else if (e.key === ',') {
          stepFrame(-1);
        } else if (e.key === '.') {
          stepFrame(1);
        }
      });
    }

    function toggleModal(id) {
      const m = document.getElementById(id);
      m.classList.toggle('hidden');
    }
  </script>
</body>
</html>
"""

out_html = os.path.join(folder, 'index.html')
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"CapCut Studio HTML with full editing tools written successfully to: {out_html}")
