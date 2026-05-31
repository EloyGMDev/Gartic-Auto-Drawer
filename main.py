python
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pyautogui
import time
from PIL import Image, ImageTk, ImageFilter
import threading
import math
import random

# Forzar máxima velocidad de ejecución de PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0

# ── PALETA REAL DE GARTIC (Mapeo de color intacto para el motor) ──
GARTIC_PALETTE = [
    (0, 0, 0), (85, 85, 85), (0, 80, 205), (255, 255, 255), (170, 170, 170),
    (38, 201, 254), (0, 128, 38), (141, 0, 0), (115, 62, 17), (0, 204, 52),
    (255, 10, 10), (255, 116, 10), (178, 126, 17), (136, 0, 77), (196, 101, 95),
    (255, 205, 10), (255, 0, 175), (255, 180, 175)
]

state = {
    "img": None,
    "canvas_region": None,
    "palette_region": None,
    "palette_cols": 3,
    "palette_rows": 6,
    "drawing": False,
    "abort": False,
    "skip_noise": True,
    "simplify_paths": True,
    "smooth_image": False,
    "draw_mode": "Líneas",
    "speed_profile": "Seguro",
}

class ActionRateLimiter:
    def __init__(self, max_actions_seguro=17, max_actions_turbo=19):
        self.max_actions_seguro = max_actions_seguro
        self.max_actions_turbo = max_actions_turbo
        self.history = []
        self.lock = threading.Lock()

    def wait_if_needed(self):
        profile = state.get("speed_profile", "Seguro")
        limit = self.max_actions_seguro if profile == "Seguro" else self.max_actions_turbo
            
        with self.lock:
            while True:
                now = time.time()
                self.history = [t for t in self.history if now - t < 1.0]
                if len(self.history) < limit:
                    self.history.append(now)
                    break
                else:
                    sleep_time = 1.01 - (now - self.history[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)

rate_limiter = ActionRateLimiter(max_actions_seguro=17, max_actions_turbo=19)

def closest_palette_color(r, g, b, palette):
    best = None
    best_dist = float('inf')
    for i, (pr, pg, pb) in enumerate(palette):
        mean_r = (r + pr) / 2.0
        delta_r = r - pr
        delta_g = g - pg
        delta_b = b - pb
        weight_r = 2.0 + mean_r / 256.0
        weight_g = 4.0
        weight_b = 2.0 + (255.0 - mean_r) / 256.0
        dist = weight_r * delta_r**2 + weight_g * delta_g**2 + weight_b * delta_b**2
        if dist < best_dist:
            best_dist = dist
            best = i
    return best

def palette_index_to_screen(idx, region, cols, rows):
    rx, ry, rw, rh = region
    col = idx % cols
    row = idx // cols
    cell_w = rw / cols
    cell_h = rh / rows
    return int(rx + (col * cell_w) + (cell_w / 2)), int(ry + (row * cell_h) + (cell_h / 2))

def click_color(idx):
    if not state["palette_region"]:
        return
    x, y = palette_index_to_screen(idx, state["palette_region"], state["palette_cols"], state["palette_rows"])
    rate_limiter.wait_if_needed()
    
    pyautogui.moveTo(x, y)
    pyautogui.mouseDown()
    if state.get("speed_profile", "Seguro") == "Seguro":
        time.sleep(random.uniform(0.025, 0.045))
    else:
        time.sleep(0.005)
    pyautogui.mouseUp()
    time.sleep(0.05)

def extract_pixels(img, region_w, region_h, step, skip_white, smooth_active):
    img = img.convert("RGBA")
    if smooth_active:
        img = img.filter(ImageFilter.MedianFilter(size=3))
    scale = min(region_w / img.width, region_h / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    offset_x, offset_y = (region_w - new_w) // 2, (region_h - new_h) // 2
    color_map = {}
    pixels = img.load()

    for y in range(0, new_h, step):
        for x in range(0, new_w, step):
            r, g, b, a = pixels[x, y]
            if a < 128 or (skip_white and r > 235 and g > 235 and b > 235):
                continue
            idx = closest_palette_color(r, g, b, GARTIC_PALETTE)
            if idx not in color_map:
                color_map[idx] = []
            color_map[idx].append((offset_x + x, offset_y + y))
    return color_map

def optimize_path_grid(pts, step, skip_noise):
    if not pts: return []
    grid = {}
    for pt in pts:
        gx, gy = pt[0] // step, pt[1] // step
        if (gx, gy) not in grid: grid[(gx, gy)] = []
        grid[(gx, gy)].append(pt)
    paths = []
    neighbor_offsets = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    
    while grid:
        curr_key = next(iter(grid))
        curr_pts = grid[curr_key]
        curr_pt = curr_pts.pop()
        if not curr_pts: del grid[curr_key]
        curr_path = [curr_pt]
        
        while True:
            found = False
            cx, cy = curr_pt
            cgx, cgy = cx // step, cy // step
            for ox, oy in neighbor_offsets:
                ngx, ngy = cgx + ox, cgy + oy
                if (ngx, ngy) in grid:
                    n_pts = grid[(ngx, ngy)]
                    best_p, best_d, best_idx = None, float('inf'), -1
                    for idx, p in enumerate(n_pts):
                        d = (cx - p[0])**2 + (cy - p[1])**2
                        if d < best_d:
                            best_d, best_p, best_idx = d, p, idx
                    if best_p:
                        curr_pt = n_pts.pop(best_idx)
                        curr_path.append(curr_pt)
                        if not n_pts: del grid[(ngx, ngy)]
                        found = True
                        break
            if not found: break
        if len(curr_path) > 1 or not skip_noise:
            paths.append(curr_path)
    return paths

def simplify_path(path, epsilon):
    if len(path) < 3: return path
    dmax, index = 0, 0
    end = len(path) - 1
    for i in range(1, end):
        x0, y0 = path[i]
        x1, y1 = path[0]
        x2, y2 = path[end]
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        den = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        dist = num / den if den != 0 else math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        if dist > dmax:
            index, dmax = i, dist
    if dmax > epsilon:
        return simplify_path(path[:index+1], epsilon)[:-1] + simplify_path(path[index:], epsilon)
    return [path[0], path[end]]

def draw_image(region, color_map, step, speed, progress_cb, status_cb):
    rx, ry, _, _ = region
    total_pts = sum(len(pts) for pts in color_map.values())
    done_pts = 0
    dur = speed / 1000.0
    sorted_colors = sorted(color_map.keys(), key=lambda k: len(color_map[k]), reverse=True)

    for idx in sorted_colors:
        if state["abort"]: break
        pts = color_map[idx]
        if not pts: continue
        if state["palette_region"]:
            click_color(idx)
            status_cb(f"Index de Color: {idx}")

        if state["draw_mode"] == "Puntos":
            for px, py in pts:
                if state["abort"]: break
                rate_limiter.wait_if_needed()
                pyautogui.moveTo(rx + px, ry + py)
                pyautogui.mouseDown()
                time.sleep(0.005 if state.get("speed_profile") == "Turbo" else random.uniform(0.005, 0.012))
                pyautogui.mouseUp()
                if state.get("speed_profile") == "Seguro":
                    time.sleep(max(0.002, dur) + random.uniform(0.003, 0.008))
                elif dur > 0:
                    time.sleep(dur)
                done_pts += 1
                if done_pts % 15 == 0: progress_cb(int(done_pts / total_pts * 100))
            continue

        paths = optimize_path_grid(pts, step, skip_noise=state["skip_noise"])
        for path in paths:
            if state["abort"]: break
            orig_len = len(path)
            if state["simplify_paths"]: path = simplify_path(path, step * 0.4)
            rate_limiter.wait_if_needed()
            
            pyautogui.moveTo(rx + path[0][0], ry + path[0][1])
            pyautogui.mouseDown()
            node_delay = max(0.008, dur) if state.get("speed_profile") == "Turbo" else random.uniform(0.024, 0.032)
            for px, py in path[1:]:
                if state["abort"]: break
                pyautogui.moveTo(rx + px, ry + py)
                if node_delay > 0: time.sleep(node_delay)
            pyautogui.mouseUp()
            if state.get("speed_profile") == "Seguro": time.sleep(random.uniform(0.08, 0.18))
            
            done_pts += orig_len
            progress_cb(int(done_pts / total_pts * 100))

    status_cb("Listo" if not state["abort"] else "Cancelado")
    state["drawing"] = False

class RegionSelector:
    def __init__(self, title, callback):
        self.callback = callback
        self.start_x = self.start_y = 0
        self.rect = None
        self.root = tk.Toplevel()
        self.root.attributes("-fullscreen", True, "-alpha", 0.4, "-topmost", True)
        self.root.configure(bg="black")
        tk.Label(self.root, text=title, fg="white", bg="black", font=("Arial", 14, "bold")).pack(pady=20)
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_press(self, e):
        self.start_x, self.start_y = e.x_root, e.y_root

    def on_drag(self, e):
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, e.x_root, e.y_root, outline="white", width=2)

    def on_release(self, e):
        x1, y1, x2, y2 = min(self.start_x, e.x_root), min(self.start_y, e.y_root), max(self.start_x, e.x_root), max(self.start_y, e.y_root)
        self.root.destroy()
        if x2 - x1 > 5 and y2 - y1 > 5: self.callback((x1, y1, x2 - x1, y2 - y1))

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gartic AutoDraw v4 - Monochromatic")
        self.root.geometry("400x790")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)
        self.build_ui()

    def build_ui(self):
        bg, fg, widget_bg = "#121212", "#ffffff", "#2c2c2c"

        # ── EXCLUSIVO BRANDING TOP LOGO HEADER ──
        logo_frame = tk.Frame(self.root, bg="#000000", bd=1, relief="solid")
        logo_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        tk.Label(logo_frame, text="eloygm.com", bg="#000000", fg="#ffffff",
                 font=("Courier New", 18, "bold")).pack(pady=(8, 2))
        tk.Label(logo_frame, text="Gartic AutoDraw v4 Pro · GitHub Edition", bg="#000000", fg="#888888",
                 font=("Arial", 9, "bold")).pack(pady=(0, 8))

        # Preview de Imagen
        frm = tk.Frame(self.root, bg=widget_bg, bd=1, relief="solid")
        frm.pack(padx=15, fill="x")
        self.preview = tk.Label(frm, bg=widget_bg, text="Click para cargar recurso de imagen",
                                fg="#aaaaaa", width=40, height=4, cursor="hand2", font=("Arial", 9, "bold"))
        self.preview.pack(padx=5, pady=5)
        self.preview.bind("<Button-1>", lambda e: self.pick_image())

        # Botones de calibración
        btn_frame = tk.Frame(self.root, bg=bg)
        btn_frame.pack(padx=15, fill="x", pady=(10, 0))
        
        tk.Button(btn_frame, text="Lienzo Gartic", command=self.select_canvas_region,
                  bg=widget_bg, fg=fg, relief="flat", font=("Arial", 9, "bold"), bd=1, highlightbackground=fg,
                  cursor="hand2", pady=6).pack(side="left", expand=True, fill="x", padx=(0, 3))
                  
        tk.Button(btn_frame, text="Paleta de Colores", command=self.select_palette_region,
                  bg=widget_bg, fg=fg, relief="flat", font=("Arial", 9, "bold"), bd=1,
                  cursor="hand2", pady=6).pack(side="right", expand=True, fill="x", padx=(3, 0))

        self.canvas_label = tk.Label(self.root, text="Lienzo: No definido", bg=bg, fg="#888888", font=("Arial", 8))
        self.canvas_label.pack(pady=1)
        self.palette_label = tk.Label(self.root, text="Paleta: No definida", bg=bg, fg="#888888", font=("Arial", 8))
        self.palette_label.pack(pady=1)

        # Perfil de Seguridad
        profile_frame = tk.LabelFrame(self.root, text=" Control de Transmisión de Datos ", bg=bg, fg=fg, font=("Arial", 9, "bold"))
        profile_frame.pack(padx=15, fill="x", pady=5)
        self.profile_var = tk.StringVar(value="Seguro")
        tk.Radiobutton(profile_frame, text="Tiempo Infinito (Filtro Humano / Seguro)", variable=self.profile_var, value="Seguro",
                       bg=bg, fg=fg, selectcolor=widget_bg, activebackground=bg, font=("Arial", 8)).pack(anchor="w", padx=10, pady=2)
        tk.Radiobutton(profile_frame, text="Turbo (Límite Máximo de Sockets)", variable=self.profile_var, value="Turbo",
                       bg=bg, fg=fg, selectcolor=widget_bg, activebackground=bg, font=("Arial", 8)).pack(anchor="w", padx=10, pady=2)

        # Modo de Dibujo
        mode_frame = tk.LabelFrame(self.root, text=" Estructura del Trazado ", bg=bg, fg=fg, font=("Arial", 9, "bold"))
        mode_frame.pack(padx=15, fill="x", pady=5)
        self.mode_var = tk.StringVar(value="Líneas")
        tk.Radiobutton(mode_frame, text="Líneas (Vectores continuos fluidos)", variable=self.mode_var, value="Líneas",
                       bg=bg, fg=fg, selectcolor=widget_bg, activebackground=bg, font=("Arial", 8)).pack(anchor="w", padx=10, pady=2)
        tk.Radiobutton(mode_frame, text="Puntos (Procesamiento píxel por píxel)", variable=self.mode_var, value="Puntos",
                       bg=bg, fg=fg, selectcolor=widget_bg, activebackground=bg, font=("Arial", 8)).pack(anchor="w", padx=10, pady=2)

        # Deslizadores / Filtros
        opts = tk.Frame(self.root, bg=bg)
        opts.pack(padx=15, fill="x", pady=5)
        self.step_var = tk.IntVar(value=4)
        self.speed_var = tk.IntVar(value=1)
        self.countdown_var = tk.IntVar(value=3)
        self.white_var = tk.BooleanVar(value=True)
        self.noise_var = tk.BooleanVar(value=True)
        self.smooth_var = tk.BooleanVar(value=False)
        self.simplify_var = tk.BooleanVar(value=True)

        self.add_slider(opts, "Grosor del Vector (Step)", self.step_var, 2, 10)
        self.add_slider(opts, "Latencia por Nodo (ms)", self.speed_var, 0, 20)
        self.add_slider(opts, "Temporizador Inicial (s)", self.countdown_var, 1, 10)

        chk_frame = tk.Frame(opts, bg=bg)
        chk_frame.pack(fill="x", pady=4)
        tk.Checkbutton(chk_frame, text="Ignorar Blanco", variable=self.white_var, bg=bg, fg=fg, selectcolor=widget_bg, font=("Arial", 8)).pack(side="left", expand=True, anchor="w")
        tk.Checkbutton(chk_frame, text="Anti-Ruido", variable=self.noise_var, bg=bg, fg=fg, selectcolor=widget_bg, font=("Arial", 8)).pack(side="left", expand=True, anchor="w")
        tk.Checkbutton(chk_frame, text="Filtro Median", variable=self.smooth_var, bg=bg, fg=fg, selectcolor=widget_bg, font=("Arial", 8)).pack(side="left", expand=True, anchor="w")
        tk.Checkbutton(chk_frame, text="RDP Rápido", variable=self.simplify_var, bg=bg, fg=fg, selectcolor=widget_bg, font=("Arial", 8)).pack(side="left", expand=True, anchor="w")

        # Barra de progreso monocromática
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Mono.Horizontal.TProgressbar", troughcolor="#2c2c2c", background="#ffffff", borderwidth=0)
        self.progress = ttk.Progressbar(self.root, style="Mono.Horizontal.TProgressbar", length=360, mode="determinate")
        self.progress.pack(pady=(10, 2))

        self.status_lbl = tk.Label(self.root, text="Sistema listo para inicialización.", bg=bg, fg="#888888", font=("Arial", 8))
        self.status_lbl.pack()

        # Botones de acción principal
        self.btn_draw = tk.Button(self.root, text="INICIAR AUTOMATIZACIÓN", command=self.start_draw,
                                  bg="#ffffff", fg="#000000", relief="flat", font=("Arial", 10, "bold"),
                                  activebackground="#aaaaaa", cursor="hand2", pady=8)
        self.btn_draw.pack(padx=15, fill="x", pady=(8, 4))

        self.btn_stop = tk.Button(self.root, text="ABORTAR", command=lambda: state.update({"abort": True}),
                                  bg=widget_bg, fg=fg, relief="flat", font=("Arial", 9, "bold"), cursor="hand2",
                                  pady=4, state="disabled")
        self.btn_stop.pack(padx=15, fill="x", pady=(0, 15))

    def add_slider(self, parent, label, var, from_, to):
        row = tk.Frame(parent, bg="#121212")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg="#121212", fg="#aaaaaa", font=("Arial", 8), width=28, anchor="w").pack(side="left")
        tk.Scale(row, from_=from_, to=to, orient="horizontal", variable=var, bg="#121212", fg=f"#ffffff", 
                 troughcolor="#2c2c2c", highlightthickness=0, length=120, showvalue=True).pack(side="right")

    def pick_image(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")])
        if not path: return
        state["img"] = Image.open(path)
        prev = state["img"].copy()
        prev.thumbnail((300, 110))
        photo = ImageTk.PhotoImage(prev)
        self.preview.configure(image=photo, text="")
        self.preview.image = photo
        self.set_status(f"Cargado: {path.split('/')[-1]}")

    def select_canvas_region(self):
        self.root.iconify()
        time.sleep(0.3)
        RegionSelector("Selecciona el Lienzo Blanco de Gartic", self._on_canvas)

    def select_palette_region(self):
        self.root.iconify()
        time.sleep(0.3)
        RegionSelector("Selecciona la Región Total de la Paleta (Grid 3x6)", self._on_palette)

    def _on_canvas(self, region):
        state["canvas_region"] = region
        self.canvas_label.configure(text=f"Lienzo: {region[2]}x{region[3]}px en ({region[0]},{region[1]})", fg="#ffffff")
        self.root.deiconify()

    def _on_palette(self, region):
        state["palette_region"] = region
        self.palette_label.configure(text=f"Paleta: Grid 3x6 en ({region[0]},{region[1]})", fg="#ffffff")
        self.root.deiconify()

    def start_draw(self):
        if not state["img"] or not state["canvas_region"]:
            messagebox.showwarning("Error", "Falta definir la imagen o el lienzo de destino.")
            return

        state["drawing"], state["abort"] = True, False
        state["skip_noise"] = self.noise_var.get()
        state["simplify_paths"] = self.simplify_var.get()
        state["smooth_image"] = self.smooth_var.get()
        state["draw_mode"] = self.mode_var.get()
        state["speed_profile"] = self.profile_var.get()
        
        self.btn_draw.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress["value"] = 0

        step, speed, skip_white, countdown = self.step_var.get(), self.speed_var.get(), self.white_var.get(), self.countdown_var.get()
        region = state["canvas_region"]

        def run():
            for i in range(countdown, 0, -1):
                self.set_status(f"Preparando entorno... Trazado en {i}s")
                time.sleep(1)
                if state["abort"]:
                    self.root.after(0, self.finish)
                    return
            self.set_status("Analizando matriz...")
            color_map = extract_pixels(state["img"], region[2], region[3], step, skip_white, state["smooth_image"])
            self.set_status("Ejecutando trazado de vectores...")
            draw_image(region, color_map, step, speed, 
                       progress_cb=lambda p: self.root.after(0, lambda: self.progress.configure(value=p)),
                       status_cb=lambda m: s
