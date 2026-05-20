import os
import cv2
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from scipy.interpolate import CubicSpline


def extraer_contorno_ala(ruta_imagen, num_puntos_deseados=70):
    img = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se encontró la imagen en: {ruta_imagen}")

    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    contornos, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    if not contornos:
        raise ValueError("No se detectó el contorno del ala.")

    ala_contorno = max(contornos, key=cv2.contourArea)
    puntos = ala_contorno.reshape(-1, 2).astype(float)

    alto_img, _ = img.shape
    puntos[:, 1] = alto_img - puntos[:, 1]

    indices = np.linspace(0, len(puntos) - 1, num_puntos_deseados, dtype=int)
    puntos_resumidos = puntos[indices]

    puntos_resumidos[-1] = puntos_resumidos[0]
    return np.vstack([puntos_resumidos, puntos_resumidos])


def simulador_pedagogico_fourier(ruta_imagen):
    puntos_control = extraer_contorno_ala(ruta_imagen)

    t = np.linspace(0, 1, len(puntos_control))
    cs_x = CubicSpline(t, puntos_control[:, 0], bc_type="periodic")
    cs_y = CubicSpline(t, puntos_control[:, 1], bc_type="periodic")

    t_fino = np.linspace(0, 1, 400)
    x_base = cs_x(t_fino)
    y_base = cs_y(t_fino)

    x_min, x_max = np.min(x_base), np.max(x_base)
    x_raiz = x_max

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    plt.subplots_adjust(bottom=0.28)

    ax1.set_aspect("equal")
    ax1.grid(True)
    (linea_ala,) = ax1.plot([], [], "b-", linewidth=2.5, label="Perfil Real")
    ax1.plot(
        x_raiz,
        y_base[np.argmax(x_base)],
        "ro",
        markersize=8,
        label="Raíz Fija",
    )
    ax1.set_xlim(x_min - 40, x_max + 40)
    ax1.set_ylim(np.min(y_base) - 150, np.max(y_base) + 150)
    ax1.set_title("Espacio Físico: Geometría del Ala")
    ax1.legend()

    ax2.grid(True)
    ax2.set_xlim(0, 3.0)
    ax2.set_ylim(-150, 150)
    ax2.set_xlabel("Tiempo (segundos)")
    ax2.set_ylabel("Amplitud de Oscilación")
    ax2.set_title("Espacio Matemático: Suma de Componentes de Fourier")

    (linea_arm1,) = ax2.plot(
        [], [], "g--", alpha=0.7, label="Armónico 1 (Fundamental)"
    )
    (linea_arm2,) = ax2.plot(
        [], [], "orange", linestyle="--", alpha=0.7, label="Armónico 2 (Ruido/Torsión)"
    )
    (linea_suma_fourier,) = ax2.plot(
        [], [], "r-", linewidth=2, label="Onda Resultante (Suma)"
    )
    ax2.legend(loc="upper right")

    tiempos_historial = []
    valores_historial = []

    ax_frec = plt.axes([0.15, 0.16, 0.70, 0.03])
    ax_amp1 = plt.axes([0.15, 0.11, 0.70, 0.03])
    ax_amp2 = plt.axes([0.15, 0.06, 0.70, 0.03])

    sl_frec = Slider(
        ax_frec, "Frecuencia Base (w)", 0.5, 3.0, valinit=1.0, valfmt="%.1f Hz"
    )
    sl_amp1 = Slider(
        ax_amp1, "Amp. Armónico 1", 10.0, 100.0, valinit=60.0, valfmt="%.0f px"
    )
    sl_amp2 = Slider(
        ax_amp2, "Amp. Armónico 2 (2w)", 0.0, 50.0, valinit=20.0, valfmt="%.0f px"
    )

    fps = 30

    def update(frame):
        tiempo = frame / fps

        frec = sl_frec.val
        a1 = sl_amp1.val
        a2 = sl_amp2.val

        w1 = 2 * np.pi * frec
        w2 = 2 * w1  # el segundo armónico tiene el doble de velocidad

        factor_distancia = (x_raiz - x_base) / (x_raiz - x_min)
        factor_distancia = np.clip(factor_distancia, 0, 1)

        desfase = -1.2 * factor_distancia

        comp1_ala = a1 * np.sin(w1 * tiempo + desfase)
        comp2_ala = a2 * np.sin(w2 * tiempo + desfase * 1.5)
        oscilacion_total = comp1_ala + comp2_ala

        y_animado = y_base + (oscilacion_total * factor_distancia)
        linea_ala.set_data(x_base, y_animado)

        tiempos_historial.append(tiempo)
        if len(tiempos_historial) > fps * 3:
            tiempos_historial.pop(0)

        t_arr = np.array(tiempos_historial)

        onda_arm1 = a1 * np.sin(w1 * t_arr)
        onda_arm2 = a2 * np.sin(w2 * t_arr)
        onda_suma = onda_arm1 + onda_arm2

        # Desplazar la ventana de tiempo
        ax2.set_xlim(max(0, tiempo - 3.0), max(3.0, tiempo))

        linea_arm1.set_data(t_arr, onda_arm1)
        linea_arm2.set_data(t_arr, onda_arm2)
        linea_suma_fourier.set_data(t_arr, onda_suma)

        return linea_ala, linea_arm1, linea_arm2, linea_suma_fourier

    ani = animation.FuncAnimation(
        fig, update, frames=int(fps * 60), interval=int(1000 / fps), blit=False
    )
    plt.suptitle(
        "¿Cómo reconstruye Fourier el aleteo?",
        fontsize=16,
        fontweight="bold",
    )
    plt.show()


if __name__ == "__main__":
    archivo_imagen = "ala.jpg"
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(carpeta_actual, archivo_imagen)

    try:
        simulador_pedagogico_fourier(ruta_completa)
    except Exception as e:
        print(f"❌ Error: {e}")
