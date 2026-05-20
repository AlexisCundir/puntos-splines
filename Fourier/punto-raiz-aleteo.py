import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

puntos = 15
x_base = np.linspace(0, 10, puntos)
y_base = np.zeros(puntos)

x_raiz = 10.0
x_punta = 0.0
factor_distancia = (x_raiz - x_base) / (x_raiz - x_punta)

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(-1, 11)
ax.set_ylim(-4, 4)
ax.grid(True, alpha=0.3)
ax.set_title("Variacion de puntos", fontweight='bold')
linea, = ax.plot([], [], 'b-', linewidth=2)
nodos = ax.scatter([], [], color='red', s=50, label="Nodos de la Estructura")
ax.plot(x_raiz, 0, 'ks', markersize=10, label="Raíz Fija (Empotramiento: Condición Y=0)")
ax.legend(loc="upper left")

fps = 30
w = 2 * np.pi * 1.0 # Frecuencia de 1 Hz

def animar(frame):
    print(frame/fps)
    tiempo = frame / fps
    
    fuerza_tiempo = 2.0 * np.sin(w * tiempo)
    
    y_animado = y_base + (fuerza_tiempo * factor_distancia)

    linea.set_data(x_base, y_animado)
    nodos.set_offsets(np.c_[x_base, y_animado])
    return linea, nodos

ani = animation.FuncAnimation(fig, animar, frames=fps, interval=1000/fps, blit=True)
plt.show()
