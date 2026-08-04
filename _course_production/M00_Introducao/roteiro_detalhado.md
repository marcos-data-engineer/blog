# 🎬 ROTEIRO DETALLADO - SECCIÓN 1
## "Gancho Inicial" (0:00 - 1:00)

**Objetivo:** Captar atención. Vender la idea. Mostrar que es posible.

---

## 📊 SLIDES NECESARIOS

### **SLIDE 1: Portada/Intro**

#### Especificaciones:

```
Duración total en pantalla: 10 segundos (0:00 - 0:10)
Tipo: Portada estilo "cine"
```

#### Visual:

```
FONDO:
Gradiente suave azul → azul claro
Inicio:  #1E40AF (azul fuerte)
Fin:     #3B82F6 (azul claro)
O alternativa: Imagen blurred de código/blog

TEXTO CENTRAL:
"¿Blog Visual, Rápido y Gratis?"

Fuente:      Montserrat Bold
Tamaño:      56pt
Color:       BLANCO (#FFFFFF)
Posición:    Centro horizontal, 40% desde arriba
Sombra:      Sombra ligera negra (2px, opacidad 30%)

EMOJIS DECORATIVOS (abajo):
💻  🚀  📝

Tamaño:      48pt cada uno
Posición:    Espaciados uniformemente abajo (20% desde pie)
Color:       BLANCO o con efecto

MÚSICA:
(Empieza aqui - ver sección música)
Fade in durante primeros 2 segundos
Volumen: -6dB
```

#### Animaciones en Google Slides:

```
Entrada:
- Fondo: Sin animación (aparece instantáneo)
- Texto: Fade in, 0.5 segundos, delay 0.5s
- Emojis: Aparecen staggered:
  - 💻 fade in a 1s
  - 🚀 fade in a 1.5s  
  - 📝 fade in a 2s

Salida (final del slide):
- Fade out, 0.5 segundos, al segundo 9
```

#### Instrucciones OBS:

```
00:00  Captura pantalla completa (1920x1080)
       Escena: "SLIDE_1_PORTADA"
       
       Si usas Google Slides:
       - Abre en navegador FULLSCREEN (F11)
       - Inicia presentación (barra espaciadora)
       - Deja en SLIDE 1
       - OBS captura esta ventana
       
00:10  Transición suave (Fade, 0.5s en OBS)
       Cambio a SLIDE 2
```

#### LO QUE DIRÁS (narración):

```
(SILENCIO TOTAL)

No hables en este slide. Solo música.
Deja que el viewer procese lo visual.

Este es tu hook - el "gancho".
La música hace el trabajo aquí.
```

#### Notas técnicas:

```
✓ NO incluyas texto pequeño (distracting)
✓ Usa SOLO logo/emojis (simple = poderoso)
✓ Mantén 10 segundos (no menos, no más)
✓ Música es 80% del impacto aquí
```

---

### **SLIDE 2: El Gancho (Contenido)**

#### Especificaciones:

```
Duración: 50 segundos (0:10 - 1:00)
Tipo: Dos columnas - Texto + Imagen
```

#### Visual:

```
LAYOUT: Dos columnas (50-50 split)

═══════════════════════════════════════════════════════════
║                                                          ║
║  COLUMNA IZQUIERDA            COLUMNA DERECHA           ║
║  (Texto - 50%)                (Imagen - 50%)            ║
║                                                          ║
═══════════════════════════════════════════════════════════

─────────────────────────────────────────────────────────

COLUMNA IZQUIERDA (Texto):

Espaciado: 60px margen izquierdo

PREGUNTA 1:
"¿Cansado de pagar"
"por hosting?"

Fuente:      Montserrat Bold
Tamaño:      40pt
Color:       #1E40AF (azul)
Posición:    Arriba-izquierda, y=80px

[ESPACIO: 20px]

PREGUNTA 2:
"¿No quieres complicarte"
"con WordPress?"

Fuente:      Montserrat Bold
Tamaño:      40pt
Color:       #1E40AF (azul)
Posición:    y=180px

[ESPACIO: 40px]

TITULAR DESTACADO:
"✓ TENEMOS BUENAS NOTICIAS"

Fuente:      Poppins Bold
Tamaño:      28pt
Color:       #F59E0B (naranja)
Posición:    y=280px
Efecto:      Checkmark es emoji ✓ verde (#10B981)

[ESPACIO: 30px]

PÁRRAFO CUERPO:
"Puedes crear un blog"
"PROFESIONAL"
"GRATIS"

Fuente:      Inter Regular
Tamaño:      24pt (normal), 32pt para "PROFESIONAL"
Color:       #374151 (gris oscuro)
Posición:    y=350px

[ESPACIO: 2px entre líneas]

─────────────────────────────────────────────────────────

COLUMNA DERECHA (Imagen):

IMAGEN PRINCIPAL:
Screenshot de tu blog: blog.dataengineer.net.br

Tamaño:      450px ancho × 350px alto
Proporciones: Fullpage screenshot (homepage)
Borde:       3px sólido #10B981 (verde)
Sombra:      Proyectada (8px, opacidad 25%)
Posición:    Centrada en columna derecha, y=60px

NOTA: Si quieres la imagen DINÁMICA (video en vivo),
ver sección "OPCIÓN 2" más abajo.
```

#### Animaciones en Google Slides:

```
Entrada del Slide 2 (desde Slide 1):

01. Fade in completo del slide: 0.5s
    Trigger: Automático al salir Slide 1

02. Columna IZQUIERDA animación:
    - Pregunta 1: Aparece fade in a 0.3s (delay 0s)
    - Pregunta 2: Aparece fade in a 0.3s (delay 0.3s)
    - "Buenas noticias": Zoom suave in a 0.5s (delay 0.8s)
    - Body text: Fade in a 0.3s (delay 1.2s)

03. Columna DERECHA animación:
    - Imagen: Slide in from right a 0.8s (delay 0.5s)
    - Borde imagen: Aparece cuando imagen

Nota: Las animaciones crean "cinematic feel"
      User sigue el flujo visual de izq a derecha

Salida del Slide 2 (final a 1:00):
    - Fade out, 0.5s, al segundo 59
```

#### Instrucciones OBS - OPCIÓN 1 (Screenshot estático):

```
00:10  Mostrar SLIDE 2
       
       Pre-grabación:
       - Captura screenshot fullpage de tu blog
       - Abre en Canva o PowerPoint
       - Ajusta tamaño y borde (3px verde)
       - Añade como imagen en slide
       
       Grabación:
       - OBS: "SLIDE_2_GANCHO"
       - Captura pantalla Google Slides fullscreen
       - Deja reproducir las animaciones
       - Deja sonar tu voz
       
00:59  Mantén visible el slide completo 49 segundos
       
01:00  Transición fade (0.5s en OBS)
       Cambio a siguiente slide
```

#### Instrucciones OBS - OPCIÓN 2 (Video en vivo - MÁS IMPACTANTE):

```
MEJOR OPCIÓN: Mostrar blog FUNCIONANDO en vivo

00:10  En lugar de screenshot:
       - Abre Chrome
       - Navega a blog.dataengineer.net.br
       - Espera carga completa
       - Muestra homepage
       
       OBS captura simultáneamente:
       
       00:10-00:15  Carga navegador (lento)
       00:15-00:30  Scroll lento por homepage
                    Muestra títulos atractivos, imágenes
       00:30-00:45  Scroll más hacia abajo
                    Muestra estructura profesional
       00:45-00:59  Pausa en algún artículo bonito
                    Deja que user vea calidad
       
01:00  Transición a siguiente slide
```

**RECOMENDACIÓN:** Opción 2 (video vivo) es MÁS impactante.
Muestra que el blog EXISTE y FUNCIONA.

---

## 🎤 NARRACIÓN COMPLETA SECCIÓN 1

### Palabra por palabra (respeta pausas):

```
[00:00-00:10]
(SILENCIO - solo música)

═══════════════════════════════════════════════════════════

[00:10-00:15]
(Voz suave, entusiasta)

"¡Hola!"

[PAUSA: 1 segundo]

"¿Cansado de pagar por hosting?"

[PAUSA: 0.5 segundos - deja que procesen]

═══════════════════════════════════════════════════════════

[00:15-00:22]

"¿No quieres complicarte con WordPress?"

[PAUSA: 1 segundo]

"Bueno... tengo buenas noticias."

[PAUSA: 0.5 segundos]

═══════════════════════════════════════════════════════════

[00:22-00:35]

"Puedes crear un blog profesional..."

[PAUSA: 0.3 segundos]

"Completamente GRATIS."

[ÉNFASIS en "GRATIS" - más lento, más fuerte]

[PAUSA: 1 segundo]

"Sin pagar un centavo por dominio."

[PAUSA: 0.3 segundos]

"Sin pagar por hosting."

[PAUSA: 0.5 segundos]

═══════════════════════════════════════════════════════════

[00:35-00:45]

"Y lo mejor..."

[PAUSA: 0.5 segundos - espera efecto dramático]

"Con una interfaz VISUAL."

[ÉNFASIS en "VISUAL" - lo importante]

[PAUSA: 1 segundo]

═══════════════════════════════════════════════════════════

[00:45-00:55]

"En este curso te voy a enseñar..."

[PAUSA: 0.3 segundos]

"Cómo crear tu primer blog utilizando GitHub Pages y Jekyll."

[PAUSA: 0.3 segundos]

"En Windows. Do cero."

[PAUSA: 0.5 segundos]

═══════════════════════════════════════════════════════════

[00:55-01:00]

"Y mira..."

[PAUSA: 0.5 segundos]

"Esto es lo que vamos a lograr hoy."

[PAUSA: fin del slide]

═══════════════════════════════════════════════════════════
```

#### Notas de dicción:

```
TONO:
✓ Entusiasta pero profesional (no predicador)
✓ Conversacional (como hablando con amigo)
✓ Enfático en palabras clave (GRATIS, blog, profesional)

VELOCIDAD:
✓ Normal - no aceleres
✓ Este es el "hook" - déjalo respirar
✓ Pausas son MÁS importantes que las palabras

PRONUNCIACIÓN (español):
✓ "CANSADO" - énfasis en primera sílaba
✓ "WordPress" - "Word-Press" (do sílabas)
✓ "GRATIS" - "GRAH-tis" (no "GRAH-tees")
✓ "Jekyll" - "He-kill" o "Je-kill" (tu elección, pero se consistente)
✓ "GitHub" - "Git-hab"
✓ "hosting" - "os-ting" (pronuncia la "o" como en "ostra")

ÉNFASIS EMOCIONAL:
✓ "GRATIS" = más fuerte, más lento (la gente pone atención)
✓ "profesional" = confianza (no dudes)
✓ "casi código" = con un toque de ironía (sonríe mientras hablas)
✓ "esto es lo que..." = esperanza, ilusión

ERRORES COMUNES (evita):
✗ No suenes como si lees (aunque leas)
✗ No aceleres al final de frase
✗ No "m" mudas (siempre pronuncia todo)
✗ No portuguizar (evita "eh", "hã")
```

---

## 🎵 MÚSICA (SECCIÓN 1)

### Timing:

```
00:00  Fade IN (2 segundos)
       Volumen: -6dB (baja)
       Comienza suave
       
00:10  FULL volumen (-3dB)
       Acompaña la narración
       Nota: Baja durante hablada
       
01:00  Fade OUT (0.5 segundos)
       Volumen vuelve a -6dB
       O desaparece si siguiente slide tiene silencio
```

### Recomendaciones de canción:

```
Características:
✓ Uplifting, pero no invasivo
✓ Tempo: 80-100 BPM (no muy rápido)
✓ Duración: Mínimo 1:30
✓ Sin voces (instrumental)
✓ Energía: Media (no demasiado dramática)

OPCIONES GRATIS:
1. "Bensound - Sunny"
   https://www.bensound.com/royalty-free-music/track/sunny
   → Perfecta para esto (optimista, limpia)

2. "Bensound - Improving"
   https://www.bensound.com/royalty-free-music/track/improving
   → Also good (motivational)

3. YouTube Audio Library:
   Busca "Corporate" o "Uplifting"
   → Montón de opciones gratis

DESCARGA ANTES DE GRABAR:
✓ Descarga MP3 a carpeta local (tipo C:\Musica\)
✓ En OBS, añade como "Audio Input Capture"
✓ Ajusta volumen a -6dB
✓ Deja que OBS sincronice con video

NO hagas streaming de Spotify/YouTube
→ Causa lag y problemas sync
```

---

## ⚙️ CONFIGURACIÓN OBS PARA ESTA SECCIÓN

### Escenas necesarias:

```
Escena 1: "SECCION_1_INTRO"
├─ Fuente: Captura de ventana Google Slides
├─ Tamaño: 1920x1080
├─ Filtros: Ninguno (natural)
└─ Micrófono: Entrada de audio (tu micrófono)

Recursos adicionales:
├─ Audio: Música "Sunny" (descargada)
├─ Video: Copia de seguridad (por si falla)
└─ Chat: Invisible (para grabación)
```

### Configuración audio:

```
Micrófono:
- Nivel: -18dB a -12dB (no clipeado)
- Sample rate: 48kHz (estándar)
- Canales: Estéreo
- Noise gate: Activado (reduce ruido fondo)

Música:
- Nivel: -6dB durante narración
- Fade in: 2 segundos
- Fade out: 0.5 segundos

Mix final:
- Voz: -6dB a -3dB (protagonista)
- Música: -12dB a -6dB (acompaña)
- Relación: 70% voz, 30% música
```

### Configuración video:

```
Codec: H.264 (x264 o NVIDIA NVENC)
Bitrate: 6000 kbps (buena calidad)
Framerate: 60 FPS grabación (exportar a 30)
Resolución: 1920x1080
Encoder: GPU si tienes (NVIDIA/AMD)
```

---

## 📹 PREP ANTES DE GRABAR

### Hardware:

```
☐ Micrófono: Conectado y probado
  - Graba 10 segundos, escúchate
  - ¿Claro? ¿Sin ruido?
  
☐ Auriculares: Conectados (para escuchar música mientras hablas)
  
☐ Monitor: 1920x1080 mínimo (para ver slides bien)
  
☐ Internet: Estable (no necesitas para esto, pero test)
```

### Software:

```
☐ Google Chrome/Firefox: Última versión
  ☐ Google Slides: Pantalla completa funciona
  
☐ OBS Studio: v30+ (actualizado)
  ☐ Avisos de meoria: Ignorados
  ☐ Escena "SECCION_1_INTRO": Creada
  ☐ Fuentes audio: Configuradas
  
☐ Música: Descargada y verificada
  - Ruta: C:\Musica\bensound-sunny.mp3
  - Duración: OK (1:30+)
  
☐ Archivo de output: Directorio preparado
  - Guardar en: C:\Videos\Seccion_1\
```

### Ambiente:

```
☐ Luz: Natural o artificial buena (sin sombras)

☐ Ruido: Cerrar ventanas, apagar AC, silencio

☐ Mascotas: Afuera o aisladas

☐ Teléfono: SILENCIO total

☐ Notificaciones Windows: Desactivadas
  - Configuración > Notificaciones > OFF
  - O modo "Focus Assist"

☐ Pantalla: Sin extensiones de Chrome que rompan diseño
  - Idealmente: Modo incógnito de Chrome
```

### Pre-grabación (5 min antes):

```
1. [ ] Abre OBS
2. [ ] Selecciona escena "SECCION_1_INTRO"
3. [ ] Test audio:
   - Habla 5 segundos en micrófono
   - Mira nivel en OBS (debería estar -18 a -12dB)
4. [ ] Abre Google Slides en Chrome fullscreen
5. [ ] Navega a SLIDE 1
6. [ ] En OBS, "Start Recording"
7. [ ] Espera 2 segundos (buffer)
8. [ ] Inicia presentación (spacebar)
9. [ ] Deja que Google Slides reproduzca
10. [ ] En el segundo 0:10, COMIENZA A HABLAR
11. [ ] Sigue el script exactamente
12. [ ] Al segundo 1:00, termina frase y espera transición
13. [ ] Stop recording
```

---

## 📝 SCRIPT IMPRIMIBLE

(Para imprimir y leer mientras grabas)

```
════════════════════════════════════════════════════════════
              SECCIÓN 1 - SCRIPT IMPRIMIBLE
═══════════════════════════════════════════════════════════

[00:00-00:10]
🔇 SILENCIO (solo música)

[00:10-00:15]
"¡Hola!"
[PAUSA 1s]
"¿Cansado de pagar por hosting?"
[PAUSA 0.5s]

[00:15-00:22]
"¿No quieres complicarte con WordPress?"
[PAUSA 1s]
"Bueno... tengo buenas noticias."
[PAUSA 0.5s]

[00:22-00:35]
"Puedes crear un blog profesional..."
[PAUSA 0.3s]
"Completamente GRATIS."
[ÉNFASIS - pausado]
[PAUSA 1s]
"Sin pagar un centavo por dominio."
[PAUSA 0.3s]
"Sin pagar por hosting."
[PAUSA 0.5s]

[00:35-00:45]
"Y lo mejor..."
[PAUSA 0.5s]
"Sin tocar casi código."
[con ironía]
[PAUSA 1s]

[00:45-00:55]
"En este curso te voy a enseñar..."
[PAUSA 0.3s]
"Cómo crear tu primer blog utilizando GitHub Pages y Jekyll."
[PAUSA 0.3s]
"En Windows. Do cero."
[PAUSA 0.5s]

[00:55-01:00]
"Y mira..."
[PAUSA 0.5s]
"Esto es lo que vamos a lograr hoy."
[fin]

════════════════════════════════════════════════════════════
TIPS DE GRABACIÓN:
✓ Lee con naturalidad (no robótico)
✓ Pausas son TAN importantes como palabras
✓ Si te equivocas, para y recomienza desde el inicio
✓ Haz 2-3 takes (luego eliges la mejor)
════════════════════════════════════════════════════════════
```

---

## ✅ CHECKLIST FINAL ANTES DE ENVIAR

Una vez que grabes esta sección, revisa:

```
AUDIO:
☐ ¿Se oye claro tu voz?
☐ ¿Hay ruido de fondo (AC, ventana, digambos)?
☐ ¿La música está a volumen correcto?
☐ ¿No hay clipping (picos de audio distorsionados)?

VIDEO:
☐ ¿Se ve Google Slides completo en pantalla?
☐ ¿Las transiciones de slides son suaves?
☐ ¿La resolución es 1920x1080 o similar?
☐ ¿Hay lag o desincronización audio/video?

CONTENIDO:
☐ ¿Todas las palabras se pronuncian claras?
☐ ¿Las pausas están en el lugar correcto?
☐ ¿El timing total es ~60 segundos?
☐ ¿La energía/entusiasmo se siente genuino?

EDICIÓN:
☐ ¿Exportaste a MP4 con buena calidad?
☐ ¿El archivo tiene tamaño normal (100-300MB)?
☐ ☐ ¿Puedes reproducir sin problemas?

SI TODO OK:
→ Sube a Google Drive
→ Comparte link conmigo
→ Te doy feedback detallado
```

---

## 📧 QUÉ ENVIARME

Cuando hayas grabado Sección 1:

1. **Archivo MP4** (resol 1280x720 o 1920x1080)
2. **Duración:** ~60 segundos
3. **Ubicación:** Google Drive (compartible)
4. **Nombre:** `Seccion_1_Gancho_[tu_nombre].mp4`
5. **Describir:** Cualquier nota sobre la grabación
   - "Primer intento, conozco que el acento..."
   - "Hice 3 takes, esta es la mejor"
   - Lo que sea relevante

---

**¡Cuando estés listo, me avisas!**

Este roteiro está detallado al máximo.

Cualquier duda sobre slides, OBS, audio, simplemente pregunta.

🚀🎬✨
