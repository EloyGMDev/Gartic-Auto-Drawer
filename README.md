# Gartic AutoDraw
Gartic AutoDraw es una herramienta de automatización avanzada diseñada para reproducir imágenes e ilustraciones de forma automática en plataformas de dibujo colaborativo como Gartic.io y Gartic Phone. Desarrollada con un enfoque híbrido de procesamiento de imágenes y simulación de hardware para evadir los sistemas heurísticos de detección de bots (anticheat).
Este proyecto ha sido optimizado y personalizado por EloyGM con una interfaz de usuario minimalista y monocromática (Dark Mode), ideal para su distribución pública en GitHub.
## Características Clave
 * **Evasión de Bloqueos (WebSocket Rate-Limiting):** Implementa un limitador de tasa mediante una ventana deslizante de tiempo (Sliding Window) que autogestiona el tráfico. Capa las peticiones de red por debajo de la barrera de seguridad de los servidores de Gartic (máximo 20 peticiones/segundo) para evitar baneos silenciosos intermitentes.
 * **Algoritmo Ramer-Douglas-Peucker (RDP):** Simplifica las curvas complejas y tramos rectos de vectores continuos. Reduce la cantidad de puntos redundantes enviados a la cola de eventos del sistema en un 70-80%, acelerando drásticamente el renderizado sin perder fidelidad geométrica.
 * **Pathfinder Espacial de Rejilla O(1):** Reordena los píxeles de la imagen utilizando un algoritmo del vecino más cercano modificado. Agrupa los colores contiguos en trazos fluidos para minimizar la acción de levantar el lápiz (mouseUp), reduciendo el lag del navegador Chrome.
 * **Ajuste de Color Perceptual (Redmean):** Mapeo de color de alta definición que utiliza pesos corregidos según la percepción ocular del ser humano (ponderando con mayor precisión el canal verde y rojo frente al azul). Asocia cada color de tu imagen original con una de las 18 casillas de la paleta estándar de Gartic de forma óptima.
 * **Interfaz Monocromática Minimalista:** Rediseño estético monocromático limpio (Blanco y Negro) optimizado para sistemas operativos en modo oscuro.
## Requisitos e Instalación
Para ejecutar este script necesitas tener instalado Python 3.10 o superior y las dependencias de control de periféricos y manipulación de imágenes.
 1. Clona este repositorio o descarga el script gartic_autodraw_v4_github.py.
 2. Instala las librerías necesarias mediante pip:
```bash
pip install pyautogui pillow

```
Nota para Linux: Es posible que necesites instalar soporte adicional para simulación de pantalla (scrot o dependencias de Tkinter según tu distribución).
## Modos de Dibujo y Perfiles de Velocidad
El script cuenta con un panel selector interactivo que te permite calibrar el comportamiento del robot según el tipo de partida:
### 1. Estructura del Trazado
 * **Líneas (Recomendado):** Agrupa los píxeles del mismo color y los traza arrastrando el ratón de forma continua. Es el modo más rápido, seguro y el único viable para terminar dibujos complejos en rondas con tiempo estándar.
 * **Puntos:** Realiza un clic directo e independiente sobre cada píxel exacto de la imagen. Es un método de puntillismo ultra preciso pero más lento, ya que cada clic individual consume un token del limitador de tasa.
### 2. Control de Transmisión de Datos (Perfiles de Velocidad)
 * **Perfil Seguro (Tiempo Infinito):** Diseñado para salas privadas con amigos donde se juega sin límite de tiempo. Envía los datos con latencias de arrastre humanas (~24ms - 32ms por punto) e introduce pausas e irregularidades periódicas realistas. Es 100% indetectable.
 * **Perfil Turbo:** Calibrado para rondas competitivas estándar de 60 segundos. Desactiva las pausas estéticas y aprieta el limitador de tasa hasta las 19 acciones por segundo (rozando el límite del servidor), permitiendo terminar piezas de arte antes de que expire el temporizador del juego.
## Explicación de los Filtros y Deslizadores
 * **Grosor del Vector (Step):** Determina el espaciado entre píxeles analizados. Un valor de 2 ofrece un nivel de detalle ultra fino pero genera más puntos. Un valor de 4 o 5 es el estándar perfecto para logos o dibujos rápidos.
 * **Latencia por Nodo (ms):** Tiempo de espera adicional por coordenada. Déjalo en 1 o 0 para máxima velocidad. Súbelo si notas que Google Chrome se congela o tiene lag.
 * **Ignorar Blanco:** Evita que el script intente "pintar" las zonas de fondo de la imagen original que ya son blancas, ahorrando un valioso tiempo en la ronda.
 * **Anti-Ruido:** Filtra píxeles huérfanos o aislados de un solo punto para que el ratón no realice micro-movimientos innecesarios de punta a punta del lienzo.
 * **Filtro Median (Suavizar):** Aplica un filtro de vecindad de píxeles para limpiar bordes aserrados. (Ver recomendaciones de uso).
 * **RDP Rápido:** Activa la simplificación de tramos vectoriales redundantes. Recomendado tenerlo siempre activo.
## Recomendaciones de Oro para un Dibujo Perfecto
### Configuración del Pincel en Gartic
 * **Usa siempre el tamaño de lápiz más fino:** Para garantizar que la resolución de renderizado calculada por el script coincida perfectamente con el trazo físico, es fundamental configurar siempre la herramienta de lápiz o pincel en la opción más fina dentro de la interfaz de Gartic.io o Gartic Phone. Si se usa un pincel grueso, el dibujo se verá borroso y los colores se superpondrán de forma caótica.
### Para dibujos lineales finos, Manga o Contornos (ej. Gojo / Cómics)
 * **DESACTIVA "Filtro Median":** El suavizado interpreta las líneas de contorno de 1 o 2 píxeles como "ruido" y las borrará antes de empezar a pintar. Mantén esta opción desmarcada para ilustraciones basadas en trazos finos.
 * Usa el modo **Líneas** con un **Step** de 3 para capturar la definición de los ojos y el rostro sin pixelar el resultado.
### Para evadir el Anticheat de Gartic Phone / Gartic.io
 * **No satures el servidor en modo puntos:** Si utilizas el modo Puntos a velocidad Turbo ilimitada en el navegador, el servidor de Gartic Phone interpretará el desborde de tramas WebSocket como un ataque de denegación de servicio y desconectará silenciosamente tu flujo de dibujo. Usa siempre el modo **Líneas** con el perfil **Tiempo Infinito (Seguro)** para dibujos de larga duración.
 * **Paso de calibración exacto:** Al definir el lienzo y la paleta de colores, arrastra el recuadro cubriendo únicamente la zona activa de forma muy precisa para evitar desvíos del ratón.
## Parada de Emergencia (Fail-Safe)
El script tiene activado el sistema de seguridad nativo de PyAutoGUI. Si el ratón se desvía, el dibujo se desfasa o deseas detener la ejecución inmediatamente, arrastra el cursor del ratón con fuerza hacia la esquina superior izquierda de tu monitor (coordenada 0,0). El script se detendrá de inmediato de forma segura.

Desarrollado y optimizado por EloyGM.
Contacto, actualizaciones y proyectos: eloygm.com
