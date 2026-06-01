<div align="center">

# Gartic AutoDraw

**Herramienta de automatización avanzada para reproducir imágenes en plataformas de dibujo colaborativo.**  
Desarrollada con procesamiento de imágenes híbrido y simulación de hardware para evadir sistemas heurísticos de detección de bots.

[![Python](https://img.shields.io/badge/python-3.10+-1f6feb?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-238636?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0-6e40c9?style=flat-square)](#)
[![Anticheat](https://img.shields.io/badge/anticheat-bypass_✓-1b7c83?style=flat-square)](#evadir-el-anticheat)
[![Platform](https://img.shields.io/badge/platform-windows_·_linux-9a6700?style=flat-square)](#requisitos-e-instalación)
[![RDP](https://img.shields.io/badge/RDP-optimized-238636?style=flat-square)](#algoritmo-ramer-douglas-peucker-rdp)

---

[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/d8ugUESXwS)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@eloygm)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/eloygumo/)
[![Website](https://img.shields.io/badge/eloygm.com-0d1117?style=for-the-badge&logo=google-chrome&logoColor=58a6ff)](https://eloygm.com)

</div>

---

## Características clave

| Característica | Descripción |
|---|---|
| **Evasión WebSocket Rate-Limit** | Sliding Window que mantiene el tráfico por debajo del límite del servidor (máx. 20 req/s) para evitar baneos silenciosos. |
| **Algoritmo Ramer-Douglas-Peucker** | Simplifica vectores continuos reduciendo puntos redundantes un **70-80%** sin perder fidelidad geométrica. |
| **Pathfinder Espacial O(1)** | Vecino más cercano modificado que agrupa colores contiguos en trazos fluidos, minimizando eventos `mouseUp`. |
| **Ajuste Perceptual Redmean** | Mapeo de color con pesos corregidos según percepción ocular humana — paleta estándar de 18 colores de Gartic. |
| **Interfaz Monocromática** | Rediseño estético limpio en blanco y negro optimizado para sistemas en modo oscuro. |

---

## Requisitos e instalación

**Requisitos:** Python 3.10 o superior · `pyautogui` · `Pillow`

```bash
# 1. Clona el repositorio
git clone https://github.com/EloyGMDev/Gartic-Auto-Drawer.git

# 2. Instala las dependencias
pip install pyautogui pillow

# 3. Ejecuta el script
python main.py
```

> **Linux:** Es posible que necesites instalar soporte adicional para simulación de pantalla (`scrot` o dependencias de Tkinter según tu distribución).

---

## Modos de dibujo

### Estructura del trazado

**Líneas** *(Recomendado)*  
Agrupa los píxeles del mismo color y los traza arrastrando el ratón de forma continua. El modo más rápido, seguro y el único viable para terminar dibujos complejos en rondas con tiempo estándar.

**Puntos**  
Realiza un clic directo e independiente sobre cada píxel exacto. Ultra preciso pero más lento — cada clic consume un token del limitador de tasa.

### Perfiles de velocidad

**Perfil Seguro — Tiempo Infinito**  
Latencias de arrastre humanas (~24ms - 32ms por punto) con pausas e irregularidades periódicas realistas. Diseñado para salas privadas sin límite de tiempo. 100% indetectable.

**Perfil Turbo**  
Calibrado para rondas competitivas de 60 segundos. Aprieta el limitador hasta las 19 acciones por segundo, rozando el límite del servidor.

---

## Filtros y parámetros

| Parámetro | Descripción |
|---|---|
| **Step (grosor del vector)** | Espaciado entre píxeles analizados. Valor `2` = ultra fino. Valor `4-5` = estándar para logos y dibujos rápidos. |
| **Latencia por nodo (ms)** | Tiempo extra por coordenada. Déjalo en `0-1` para máxima velocidad. Súbelo si Chrome se congela. |
| **Ignorar Blanco** | Omite zonas de fondo blancas de la imagen original, ahorrando tiempo por ronda. |
| **Anti-Ruido** | Filtra píxeles huérfanos aislados para evitar micro-movimientos innecesarios del ratón. |
| **Filtro Median** | Suaviza bordes aserrados. Desactivar para dibujos con líneas finas o estilo manga. |
| **RDP Rápido** | Simplifica tramos vectoriales redundantes. Se recomienda mantenerlo siempre activo. |

---

## Recomendaciones

### Configuración del pincel en Gartic

Usa siempre el **tamaño de lápiz más fino** disponible. Si se usa un pincel grueso, el dibujo se verá borroso y los colores se superpondrán de forma caótica.

### Para lineart, manga o contornos

- **Desactiva el Filtro Median** — el suavizado interpreta las líneas de 1-2 px como ruido y las borrará.
- Usa el modo **Líneas** con un **Step de 3** para capturar la definición de ojos y rostro sin pixelar el resultado.

### Evadir el anticheat

- No uses el modo **Puntos** a velocidad **Turbo** — el servidor de Gartic Phone lo interpretará como un flood de WebSocket y desconectará el flujo de dibujo silenciosamente.
- Para dibujos de larga duración usa siempre **Líneas** + **Perfil Seguro**.

---

## Fail-Safe de emergencia

El script tiene activado el sistema de seguridad nativo de PyAutoGUI.

> Si el ratón se desfasa o deseas detener la ejecución inmediatamente, arrastra el cursor con fuerza hacia la **esquina superior izquierda del monitor (coordenada 0, 0)**. El script se detendrá de forma segura e inmediata.

---

## Nota sobre la selección de áreas

Al arrastrar el recuadro para seleccionar el lienzo o la paleta, la línea roja puede aparecer ligeramente desplazada respecto al cursor. Esto es un desfase puramente visual causado por el escalado de pantalla DPI de Windows en Tkinter. Las coordenadas registradas son las del cursor real — la selección final es totalmente precisa.

---

<div align="center">

Desarrollado y optimizado por **EloyGM**  
Contacto, actualizaciones y proyectos: [eloygm.com](https://eloygm.com)

</div>
