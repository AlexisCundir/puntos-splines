import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import tkinter as tk
from tkinter import simpledialog

class LaboratorioNodosFourierPegar:
    def __init__(self):
        # 1. Configurar la ventana gráfica de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(11, 7))
        plt.subplots_adjust(bottom=0.35)
        
        self.ax.set_xlim(-0.5, 10.5)
        self.ax.set_ylim(-5, 5)
        self.ax.grid(True, alpha=0.5)
        self.ax.set_title("Laboratorio Numérico: Animación de Nodos por Fourier", 
                          fontweight='bold', fontsize=12)
        
        # 2. Definición de la Viga Discreta (Los Nodos)
        self.num_puntos = 40
        self.x_base = np.linspace(0, 10, self.num_puntos)
        self.y_base = np.zeros(self.num_puntos)
        
        self.linea_viga, = self.ax.plot([], [], 'b-', alpha=0.4, linewidth=2)
        self.puntos_nodos = self.ax.scatter([], [], color='red', s=40, zorder=3, label="Nodos Discretos")
        
        self.ax.plot(10, 0, 'ks', markersize=10, label="Anclaje Fijo (Y=0)")
        self.ax.legend(loc="upper left")
        
        # Física base
        self.tiempo = 0.0
        self.fps = 30
        self.formula_actual = "2*sin(w*t) + 0.8*sin(3*w*t)"
        
        # Ocultar la ventana principal invisible de Tkinter (necesaria para los diálogos)
        self.root = tk.Tk()
        self.root.withdraw()

        # 3. --- DISEÑO DE LOS CONTROLES INTERACTIVOS ---
        # Botón para abrir la ventana de copiado/pegado
        ax_boton = plt.axes([0.35, 0.24, 0.30, 0.05])
        self.btn_formula = Button(ax_boton, 'Cambiar Fórmula')
        self.btn_formula.on_clicked(self.abrir_dialogo_pegar)
        
        # Deslizadores
        ax_w = plt.axes([0.20, 0.15, 0.65, 0.03])
        ax_flex = plt.axes([0.20, 0.09, 0.65, 0.03])
        
        self.sl_w = Slider(ax_w, 'Frecuencia (w)', 0.5, 5.0, valinit=2.0, valfmt='%.1f Hz')
        self.sl_flex = Slider(ax_flex, 'Flexibilidad', 0.0, 2.0, valinit=0.8, valfmt='%.1f')
        
        # Imprimir fórmula inicial en el subtítulo
        self.actualizar_subtitulo_formula()

        # 4. Iniciar temporizador
        self.timer = self.fig.canvas.new_timer(interval=int(1000 / self.fps))
        self.timer.add_callback(self.bucle_simulacion)
        self.timer.start()

    def abrir_dialogo_pegar(self, event):
        """Abre un cuadro de diálogo del sistema operativo que sí acepta Ctrl+V."""
        # Solicitar texto al usuario mediante una ventana emergente nativa
        nueva_formula = simpledialog.askstring(
            "Entrada Matemática de Fourier", 
            "Escribe o pega (Ctrl+V) la fórmula usando las variables 'w' y 't':",
            initialvalue=self.formula_actual
        )
        
        # Si el usuario no canceló y el cuadro no está vacío, actualizar
        if nueva_formula:
            self.formula_actual = nueva_formula.strip()
            self.actualizar_subtitulo_formula()

    def actualizar_subtitulo_formula(self):
        self.ax.set_title(f"Fórmula activa: {self.formula_actual}", color='purple', fontweight='bold', fontsize=11)

    def bucle_simulacion(self):
        self.tiempo += 1.0 / self.fps
        
        w = self.sl_w.val
        flex = self.sl_flex.val
        t = self.tiempo
        
        factor_distancia = (10.0 - self.x_base) / 10.0
        
        try:
            ambiente_eval = {
                'sin': np.sin, 'cos': np.cos, 'pi': np.pi,
                't': t, 'w': w, 'np': np
            }
            
            # Evaluación de la serie numérica ingresada
            oscilacion_temporal = eval(self.formula_actual, {"__builtins__": None}, ambiente_eval)
            
            desfase_estructural = -flex * factor_distancia
            y_animado = self.y_base + (oscilacion_temporal * np.cos(desfase_estructural) * factor_distancia)
            
            self.linea_viga.set_data(self.x_base, y_animado)
            self.puntos_nodos.set_offsets(np.c_[self.x_base, y_animado])
            
        except Exception:
            self.ax.set_title("⚠️ Error numérico o de sintaxis en la fórmula", color='red', fontweight='bold')
            
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    lab = LaboratorioNodosFourierPegar()
    plt.show()
