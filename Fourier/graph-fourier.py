import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import tkinter as tk  # Requerido para acceder al portapapeles del sistema

class SintetizadorFourier:
    def __init__(self):
        # Inicializar una ventana oculta de Tkinter para gestionar el portapapeles
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Variable para almacenar la fórmula en texto plano para el script de los nodos
        self.formula_plana = "0"

        # Crear la figura y una cuadrícula (Grid) para organizar los paneles
        self.fig = plt.figure(figsize=(15, 8))
        self.gs = self.fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3, bottom=0.35)
        
        # Paneles gráficos superiores
        self.ax_resultado = self.fig.add_subplot(self.gs[0:2, 0:2]) # Panel grande para la onda final
        self.ax_formula = self.fig.add_subplot(self.gs[0:2, 2])     # Panel para escribir la ecuación
        
        # Paneles gráficos inferiores (Armónicos individuales)
        self.ax_arm1 = self.fig.add_subplot(self.gs[2, 0])
        self.ax_arm2 = self.fig.add_subplot(self.gs[2, 1])
        self.ax_arm3 = self.fig.add_subplot(self.gs[2, 2])
        
        # Configurar Panel de Onda Resultante (Tiempo)
        self.ax_resultado.set_xlim(0, 1.0)
        self.ax_resultado.set_ylim(-6, 6)
        self.ax_resultado.set_title("Onda Resultante (Suma de los Armónicos)", fontweight='bold', color='darkblue')
        self.ax_resultado.grid(True)
        self.linea_suma, = self.ax_resultado.plot([], [], 'r-', linewidth=3, label="y(t) Total")
        self.ax_resultado.legend(loc="upper right")
        
        # Configurar Panel de Texto para Fórmulas
        self.ax_formula.axis('off')
        self.ax_formula.set_title("Ecuación de Fourier", fontweight='bold', color='purple')
        self.texto_ecuacion = self.ax_formula.text(0.05, 0.5, "", fontsize=10, family='monospace', va='center')
        
        # Configurar Paneles de Armónicos individuales
        self.configurar_subgrafico(self.ax_arm1, "Armónico 1 (Fundamental: 1 Hz)", 'green')
        self.configurar_subgrafico(self.ax_arm2, "Armónico 2 (2 Hz)", 'orange')
        self.configurar_subgrafico(self.ax_arm3, "Armónico 3 (3 Hz)", 'magenta')
        
        self.l_arm1, = self.ax_arm1.plot([], [], 'g-', linewidth=2)
        self.l_arm2, = self.ax_arm2.plot([], [], 'o-', color='orange', markersize=0.5, linewidth=2)
        self.l_arm3, = self.ax_arm3.plot([], [], 'b-', color='magenta', linewidth=2)
        
        # Vector de tiempo discreto fino para el cálculo
        self.t = np.linspace(0, 1.0, 400)
        
        # --- DISEÑO DE LOS SLIDERS EN LA BASE DE LA VENTANA ---
        # Componente continua a0
        self.ax_a0 = plt.axes([0.15, 0.28, 0.70, 0.025])
        self.sl_a0 = Slider(self.ax_a0, 'Offset (a0/2)', -3.0, 3.0, valinit=0.0, valfmt='%.1f px')
        
        # Controles Armónico 1 (Frecuencia = 1 Hz)
        self.ax_a1 = plt.axes([0.15, 0.23, 0.30, 0.025])
        self.ax_p1 = plt.axes([0.55, 0.23, 0.30, 0.025])
        self.sl_a1 = Slider(self.ax_a1, 'Amp 1', 0.0, 3.0, valinit=2.0, valfmt='%.1f')
        self.sl_p1 = Slider(self.ax_p1, 'Fase 1 (rad)', -np.pi, np.pi, valinit=0.0, valfmt='%.2f')
        
        # Controles Armónico 2 (Frecuencia = 2 Hz)
        self.ax_a2 = plt.axes([0.15, 0.18, 0.30, 0.025])
        self.ax_p2 = plt.axes([0.55, 0.18, 0.30, 0.025])
        self.sl_a2 = Slider(self.ax_a2, 'Amp 2', 0.0, 3.0, valinit=0.0, valfmt='%.1f')
        self.sl_p2 = Slider(self.ax_p2, 'Fase 2 (rad)', -np.pi, np.pi, valinit=0.0, valfmt='%.2f')
        
        # Controles Armónico 3 (Frecuencia = 3 Hz)
        self.ax_a3 = plt.axes([0.15, 0.13, 0.30, 0.025])
        self.ax_p3 = plt.axes([0.55, 0.13, 0.30, 0.025])
        self.sl_a3 = Slider(self.ax_a3, 'Amp 3', 0.0, 3.0, valinit=0.0, valfmt='%.1f')
        self.sl_p3 = Slider(self.ax_p3, 'Fase 3 (rad)', -np.pi, np.pi, valinit=0.0, valfmt='%.2f')
        
        # --- BOTÓN DE COPIADO ---
        self.ax_boton = plt.axes([0.40, 0.04, 0.20, 0.05])
        self.btn_copiar = Button(self.ax_boton, '📋 Copiar Fórmula', color='lightblue', hovercolor='skyblue')
        self.btn_copiar.on_clicked(self.copiar_al_portapapeles)

        # Enlazar todos los sliders a la función de refresco dinámico
        sliders = [self.sl_a0, self.sl_a1, self.sl_p1, self.sl_a2, self.sl_p2, self.sl_a3, self.sl_p3]
        for s in sliders:
            s.on_changed(self.actualizar_onda)
            
        # Calcular por primera vez al abrir
        self.actualizar_onda(None)

    def configurar_subgrafico(self, ax, titulo, color):
        ax.set_xlim(0, 1.0)
        ax.set_ylim(-3.5, 3.5)
        ax.grid(True, alpha=0.4)
        ax.set_title(titulo, fontsize=9, fontweight='bold', color=color)

    def copiar_al_portapapeles(self, event):
        """Guarda la ecuación de una sola línea en el portapapeles del sistema operativo."""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.formula_plana)
        self.root.update()  # Mantener los datos después de cerrar la ventana
        # Modificar temporalmente el título del botón para dar feedback visual
        self.btn_copiar.label.set_text("¡Copiado con éxito!")
        self.fig.canvas.draw_idle()

    def actualizar_onda(self, val):
        # Resetear texto del botón cuando se mueva un slider
        self.btn_copiar.label.set_text("📋 Copiar Fórmula")

        # 1. Leer variables desde los deslizadores
        a0 = self.sl_a0.val
        amp1, fase1 = self.sl_a1.val, self.sl_p1.val
        amp2, fase2 = self.sl_a2.val, self.sl_p2.val
        amp3, fase3 = self.sl_a3.val, self.sl_p3.val
        
        # 2. Calcular ondas individuales
        onda1 = amp1 * np.sin(2 * np.pi * 1 * self.t + fase1)
        onda2 = amp2 * np.sin(2 * np.pi * 2 * self.t + fase2)
        onda3 = amp3 * np.sin(2 * np.pi * 3 * self.t + fase3)
        y_total = a0 + onda1 + onda2 + onda3
        
        # 3. Refrescar hilos gráficos
        self.l_arm1.set_data(self.t, onda1)
        self.l_arm2.set_data(self.t, onda2)
        self.l_arm3.set_data(self.t, onda3)
        self.linea_suma.set_data(self.t, y_total)
        
        # 4. Convertir a Coeficientes trigonométricos (a_k y b_k)
        a1_trig, b1_trig = amp1 * np.sin(fase1), amp1 * np.cos(fase1)
        a2_trig, b2_trig = amp2 * np.sin(fase2), amp2 * np.cos(fase2)
        a3_trig, b3_trig = amp3 * np.sin(fase3), amp3 * np.cos(fase3)
        
        # 5. CONSTRUCCIÓN DE LA FÓRMULA DE TEXTO PLANO (UNA SOLA LÍNEA SEGUIDA)
        # Iniciamos con la componente continua si es distinta de cero
        partes_formula = []
        if abs(a0) > 0.01:
            partes_formula.append(f"{a0:.2f}")
            
        def agregar_terminos(freq, ak, bk):
            terminos = []
            if abs(ak) > 0.01:
                terminos.append(f"{'+' if ak>=0 and partes_formula else ''}{ak:.2f}*cos(2*pi*{freq}*t)")
            if abs(bk) > 0.01:
                terminos.append(f"{'+' if bk>=0 and (partes_formula or terminos) else ''}{bk:.2f}*sin(2*pi*{freq}*t)")
            return terminos

        if amp1 > 0.01: partes_formula.extend(agregar_terminos(1, a1_trig, b1_trig))
        if amp2 > 0.01: partes_formula.extend(agregar_terminos(2, a2_trig, b2_trig))
        if amp3 > 0.01: partes_formula.extend(agregar_terminos(3, a3_trig, b3_trig))
        
        # Unir todos los fragmentos. Si todo es 0, la ecuación es simplemente "0"
        self.formula_plana = " ".join(partes_formula).replace("+ -", "- ").replace("- -", "+ ")
        if not self.formula_plana.strip():
            self.formula_plana = "0"

        # 6. Imprimir la vista multilínea tradicional en la pantalla (Interfaz gráfica)
        texto_math = f"FÓRMULA ANALÍTICA:\n\n"
        texto_math += f"y(t) = {a0:.2f} (a0/2)\n"
        if amp1 > 0.01:
            texto_math += f"   {'+' if a1_trig>=0 else '-'} {abs(a1_trig):.2f}*cos(2*pi*1*t)\n"
            texto_math += f"   {'+' if b1_trig>=0 else '-'} {abs(b1_trig):.2f}*sin(2*pi*1*t)\n"
        if amp2 > 0.01:
            texto_math += f"   {'+' if a2_trig>=0 else '-'} {abs(a2_trig):.2f}*cos(2*pi*2*t)\n"
            texto_math += f"   {'+' if b2_trig>=0 else '-'} {abs(b2_trig):.2f}*sin(2*pi*2*t)\n"
        if amp3 > 0.01:
            texto_math += f"   {'+' if a3_trig>=0 else '-'} {abs(a3_trig):.2f}*cos(2*pi*3*t)\n"
            texto_math += f"   {'+' if b3_trig>=0 else '-'} {abs(b3_trig):.2f}*sin(2*pi*3*t)\n"
            
        self.texto_ecuacion.set_text(texto_math)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    app = SintetizadorFourier()
    plt.suptitle("Modelado de Ondas por Series de Fourier", fontsize=14, fontweight='bold')
    plt.show()
