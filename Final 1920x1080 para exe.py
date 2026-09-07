import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter.font as tkFont
import random, time, os
import pygame

# 🧩 RUTA COMPATIBLE CON PYINSTALLER
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

NIVELES = {
    (1, 2): 4,
    (3, 4): 6,
    (5, 6): 8,
    (7, 8): 10,
    (9, 10): 12
}

class Memoria:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Memoria")
        
        self.ancho_ventana = self.root.winfo_screenwidth()
        self.alto_ventana = self.root.winfo_screenheight()
        self.root.geometry(f"{self.ancho_ventana}x{self.alto_ventana}")

        # 🔹 Opcional: para evitar que el usuario cambie la ventana
        self.root.resizable(False, False)

        # Fondo de inicio
        self.fondo = ImageTk.PhotoImage(Image.open(os.path.join("imagenes", "fondo_inicio.png")).resize((1920, 1080)))
        self.inicio_frame = tk.Frame(root, width=1920, height=1080)
        tk.Label(self.inicio_frame, image=self.fondo).place(x=0, y=0)

        # Botón de inicio
        self.img_boton_inicio = ImageTk.PhotoImage(
            Image.open(os.path.join("imagenes", "boton_inicio.png")).resize((300, 100))
        )
        tk.Button(self.inicio_frame, image=self.img_boton_inicio,
                  command=self.start_juego, borderwidth=0,
                  highlightthickness=0, takefocus=0, relief="flat").place(relx=0.5, rely=0.75, anchor="center")

        # Puntuación más alta
        self.puntaje_mas_alto = self.obtener_puntaje_maximo()
        self.label_puntaje = tk.Label(self.inicio_frame,
                                      text=f"Puntuación más alta: {self.puntaje_mas_alto}",
                                      font=("felix titling", 18), bg="#0D2E3A", fg="white")
        self.label_puntaje.place(relx=0.5, rely=0.85, anchor="center")
        self.inicio_frame.pack()

    def start_juego(self):
        self.inicio_frame.destroy()
        self.nivel = tk.IntVar(value=1)
        self.puntaje = 0
        self.nuevo_record = False
        self.setup_nivel()

    def cartas_por_nivel(self):
        lv = self.nivel.get()
        for (i, j), cant in NIVELES.items():
            if i <= lv <= j:
                return cant if cant % 2 == 0 else cant + 1
        return 12

    def setup_nivel(self):
        self.cartas_resueltas = []
        self.tiempo_restante = 19

        try:
            self.root.after_cancel(self.temporizador_id)
        except AttributeError:
            pass

        self.cant_cartas = self.cartas_por_nivel()
        num_pares = self.cant_cartas // 2
        imagenes = [f"carta{k+1}.png" for k in range(num_pares)]
        self.lista_cartas = imagenes * 2
        random.shuffle(self.lista_cartas)

        fondo_nivel = f"fondo_nivel{self.nivel.get()}.png"
        if os.path.exists(os.path.join("imagenes", fondo_nivel)):
            self.fondo_actual = ImageTk.PhotoImage(Image.open(os.path.join("imagenes", fondo_nivel)).resize((1920, 1080)))
        else:
            self.fondo_actual = self.fondo

        self.tablero = tk.Frame(self.root, width=1920, height=1080)
        tk.Label(self.tablero, image=self.fondo_actual).place(x=0, y=0)

        self.reverso = ImageTk.PhotoImage(Image.open(os.path.join("imagenes", "reverso.png")).resize((240, 400)))
        self.imagenes_carta = {}
        for img in set(self.lista_cartas):
            im = Image.open(os.path.join("imagenes", img)).resize((240, 400))
            self.imagenes_carta[img] = ImageTk.PhotoImage(im)

        self.botones = []
        self.seleccion = []
        self.valores = {}

        filas = 2
        columnas = self.cant_cartas // 2
        espacio_x = 260
        espacio_y = 410
        total_ancho = columnas * espacio_x
        total_alto = filas * espacio_y
        offset_x = (1600 - total_ancho) // 2
        offset_y = (1080 - total_alto) // 2 + 30

        for i in range(filas):
            fila = []
            for j in range(columnas):
                idx = i * columnas + j
                if idx >= len(self.lista_cartas): break
                lbl = tk.Label(self.tablero,
                            image=self.reverso,
                            bg=self.tablero["bg"],
                            borderwidth=0,
                            highlightthickness=0)
                lbl.bind("<Button-1>", lambda e, i=i, j=j: self.mostrar(i, j))
                lbl.place(x=offset_x + j * espacio_x, y=offset_y + i * espacio_y)

                fila.append(lbl)
                self.valores[(i, j)] = self.lista_cartas[idx]
            self.botones.append(fila)


        self.temporizador_label = tk.Label(
            self.tablero,
            text=f"Tiempo\n{self.tiempo_restante}",
            font=("felix titling", 24),
            bg="#0D2334",
            fg="white",
            justify="center"
        )
        self.temporizador_label.place(x=1740, y=360, anchor="center")

        self.temporizador_id = self.root.after(1000, self.actualizar_tiempo)

        self.img_boton_rendirse = ImageTk.PhotoImage(
            Image.open(os.path.join("imagenes", "boton_rendirse.png")).resize((250, 80))
        )
        tk.Button(self.tablero, image=self.img_boton_rendirse,
                command=self.volver_a_inicio, borderwidth=0,
                highlightthickness=0, takefocus=0, relief="flat").place(x=1630, y=900)

        self.tablero.pack()

        
    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            # Actualizamos el texto del temporizador
            self.temporizador_label.config(text=f"Tiempo\n{self.tiempo_restante}")

            # Parpadeo en los últimos 10 segundos
            if self.tiempo_restante <= 10:
                color = "red" if self.tiempo_restante % 2 == 0 else "white"
                self.temporizador_label.config(fg=color, font=("felix titling", 26, "bold"))
            else:
                self.temporizador_label.config(fg="white", font=("felix titling", 24))

            self.tiempo_restante -= 1
            self.temporizador_id = self.root.after(1000, self.actualizar_tiempo)
        else:
            # Fin de tiempo
            messagebox.showinfo("Tiempo agotado", "Gracias por jugar!.")

            # Limpiamos correctamente y volvemos al inicio
            if hasattr(self, 'tablero'):
                self.tablero.destroy()
            self.actualizar_puntaje_maximo()
            

            

    def mostrar(self, i, j):
        if len(self.seleccion) < 2 and (i, j) not in self.cartas_resueltas and (i, j) not in self.seleccion:
            img_name = self.valores[(i, j)]
            self.botones[i][j].config(image=self.imagenes_carta[img_name])
            self.seleccion.append((i, j))
            if len(self.seleccion) == 2:
                self.root.after(300, self.comparar)


    def comparar(self):
        (i1, j1), (i2, j2) = self.seleccion
        if self.valores.get((i1, j1)) == self.valores.get((i2, j2)):
            self.puntaje += 1
            self.cartas_resueltas.extend([(i1, j1), (i2, j2)])
        else:
            self.botones[i1][j1].config(image=self.reverso)
            self.botones[i2][j2].config(image=self.reverso)
        self.seleccion = []

        # Si todas las cartas están resueltas, pasar de nivel
        if len(self.cartas_resueltas) == self.cant_cartas:
            self.nivel.set(self.nivel.get() + 1)
            self.tablero.destroy()
            if self.nivel.get() > 12:
                self.fin_del_juego()
            else:
                self.setup_nivel()

    def volver_a_inicio(self):
        try:
            if hasattr(self, 'tablero'):
                self.tablero.destroy()
        except:
            pass
        self.actualizar_puntaje_maximo()
        self.mostrar_pantalla_inicio()


    def mostrar_pantalla_inicio(self):
        # Intentar destruir frames previos si existen
        try:
            if hasattr(self, 'tablero'):
                self.tablero.destroy()
        except:
            pass

        # Crear frame de inicio
        self.inicio_frame = tk.Frame(self.root, width=1920, height=1080)
        tk.Label(self.inicio_frame, image=self.fondo).place(x=0, y=0)

        # Botón de inicio
        tk.Button(self.inicio_frame, image=self.img_boton_inicio,
                command=self.start_juego, borderwidth=0,
                highlightthickness=0, takefocus=0, relief="flat").place(relx=0.5, rely=0.75, anchor="center")

        # Texto de puntuación más alta
        self.puntaje_mas_alto = self.obtener_puntaje_maximo()
        self.label_puntaje = tk.Label(self.inicio_frame,
                                    text=f"Puntuación más alta: {self.puntaje_mas_alto}",
                                    font=("felix titling", 18), bg="#0D2E3A", fg="white")
        self.label_puntaje.place(relx=0.5, rely=0.85, anchor="center")

        # Mostrar el frame
        self.inicio_frame.pack()

    def fin_del_juego(self):
        nuevo_record = False
        if self.puntaje > self.puntaje_mas_alto:
            nuevo_record = True
            self.puntaje_mas_alto = self.puntaje
            self.animar_confetis()
        self.actualizar_puntaje_maximo()
        msg = f"Juego completo. Puntaje final: {self.puntaje}"
        if nuevo_record:
            msg += "\n¡Nuevo récord!"
        messagebox.showinfo("Fin del juego", msg)
        self.root.destroy()

    def actualizar_puntaje_maximo(self):
        with open("puntajes.txt", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Nivel alcanzado: {self.nivel.get()-1}, Puntaje: {self.puntaje}\n")

    def obtener_puntaje_maximo(self):
        if not os.path.exists("puntajes.txt"):
            return 0
        maximo = 0
        with open("puntajes.txt", "r") as f:
            for linea in f:
                try:
                    partes = linea.strip().split("Puntaje:")
                    if len(partes) > 1:
                        puntos = int(partes[1].strip())
                        maximo = max(maximo, puntos)
                except:
                    continue
        return maximo

if __name__ == "__main__":
    root = tk.Tk()
    juego = Memoria(root)
    root.mainloop()
