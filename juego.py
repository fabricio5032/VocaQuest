import pygame
import random
import sys
import tkinter as tk
from tkinter import font as tk_font

# Definir las variables del juego
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

# Inicializar Pygame
pygame.init()

# Crear la pantalla
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Test Vocacional Bros")

# Reloj
reloj = pygame.time.Clock()

# Cargar imágenes
personaje = pygame.image.load("assets/personaje.png")
personaje = pygame.transform.scale(personaje, (50, 75))
personaje_rect = personaje.get_rect()
altura_personaje = ALTO_PANTALLA - personaje_rect.height  # Altura del personaje en el suelo
personaje_rect.midbottom = (ANCHO_PANTALLA // 2, altura_personaje)  # Posición inicial del personaje
bloque = pygame.image.load("assets/bloque.png")
bloque = pygame.transform.scale(bloque, (50, 50))
fondo = pygame.image.load("assets/fondo.png")
fondo = pygame.transform.scale(fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))

# Velocidades
velocidad_personaje_x = 0
velocidad_personaje_y = 0
gravedad = 0.5

# Variables adicionales para el salto
saltando = False
velocidad_salto = -18  # Aumentar la velocidad de salto

# Preguntas
preguntas = []
preguntas_usadas = []  # Lista para almacenar las preguntas ya utilizadas
with open("assets/preguntas.txt", "r", encoding="utf-8") as archivo:
    pregunta_actual = None
    opciones_actuales = []
    for linea in archivo:
        linea = linea.strip()
        if linea.startswith("Pregunta:"):
            if pregunta_actual is not None:
                preguntas.append((pregunta_actual, opciones_actuales))
                opciones_actuales = []
            pregunta_actual = linea[len("Pregunta: "):]
        elif linea.startswith("Opción"):
            opcion = linea[len("Opción "):]
            opciones_actuales.append(opcion)
        elif linea:
            area_vocacional = linea
            preguntas.append((pregunta_actual, opciones_actuales, area_vocacional))
            pregunta_actual = None
            opciones_actuales = []

# Dividir la lista de preguntas en lotes de 10
lotes_preguntas = [preguntas[i:i+10] for i in range(0, len(preguntas), 10)]

# Áreas vocacionales
areas_vocacionales = {
    "C": "Área Administrativa",
    "H": "Área de Humanidades y Ciencias Sociales y Jurídicas",
    "A": "Área Artística",
    "S": "Área de Ciencias de la Salud",
    "I": "Área de Enseñanzas Técnicas",
    "D": "Área de Defensa y Seguridad",
    "E": "Área de Ciencias Experimentales"
}

# Registro de respuestas del usuario
respuestas_usuario = []

# Vidas
vidas = 3

# Contador de bloques tocados
bloques_tocados = 0

# Juego terminado
juego_terminado = False

# Índice del lote actual
indice_lote_actual = 0

def reiniciar_juego():
    global bloques, pregunta_actual, respuesta_actual, vidas, saltando, velocidad_personaje_y, bloques_tocados, juego_terminado, preguntas_usadas, respuestas_usuario, indice_lote_actual

    # Reiniciar bloques
    indice_lote_actual = 0
    bloques = generar_bloques()

    # Reiniciar variables
    pregunta_actual = None
    respuesta_actual = None
    vidas = 3
    saltando = False
    velocidad_personaje_y = 0
    bloques_tocados = 0
    juego_terminado = False
    preguntas_usadas = []  # Reiniciar la lista de preguntas usadas
    respuestas_usuario = []  # Reiniciar el registro de respuestas del usuario

def generar_bloques():
    bloques = []
    preguntas_disponibles = lotes_preguntas[indice_lote_actual]
    posicion_x = 50
    posicion_y = 250
    distancia_entre_bloques = 70
    for pregunta in preguntas_disponibles:
        bloque_rect = bloque.get_rect()
        bloque_rect.topleft = (posicion_x, posicion_y)
        bloques.append((bloque_rect, pregunta))
        posicion_x += distancia_entre_bloques
    return bloques

def mostrar_pregunta(pregunta, opciones, area_vocacional):
    ventana_pregunta = tk.Toplevel(root)
    ventana_pregunta.title("Pregunta")

    font_defecto = tk_font.nametofont("TkDefaultFont")
    tamano_fuente = font_defecto.cget("size")

    label_pregunta = tk.Label(ventana_pregunta, text=pregunta, font=(None, int(tamano_fuente * 1.2)))
    label_pregunta.pack(pady=10)

    opcion_var = tk.StringVar()
    opcion_var.set("")  # Inicializar la variable con una cadena vacía
    for i, opcion in enumerate(opciones, start=1):
        radio_button = tk.Radiobutton(ventana_pregunta, text=f"{i}) {opcion}", variable=opcion_var, value=opcion, font=(None, tamano_fuente), anchor="w")
        radio_button.pack(fill="x", padx=20)

    def responder():
        opcion_seleccionada = opcion_var.get()
        respuesta_usuario = (opcion_seleccionada == "Sí")
        respuestas_usuario.append((area_vocacional, respuesta_usuario))
        ventana_pregunta.destroy()

    boton_responder = tk.Button(ventana_pregunta, text="Responder", command=responder)
    boton_responder.pack(pady=10)

    # Centrar la ventana de preguntas
    ventana_pregunta.update_idletasks()
    ancho_ventana = ventana_pregunta.winfo_reqwidth()
    alto_ventana = ventana_pregunta.winfo_reqheight()
    x = (root.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y = (root.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana_pregunta.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    ventana_pregunta.focus_force()
    ventana_pregunta.grab_set()
    ventana_pregunta.wait_window()

def mostrar_area_vocacional():
    def cerrar_ventana():
        ventana_area.destroy()
        pygame.quit()

    # Calcular el área vocacional predominante
    areas_puntuacion = {area: 0 for area in areas_vocacionales.values()}
    for area_vocacional, respuesta in respuestas_usuario:
        if respuesta:
            areas_puntuacion[areas_vocacionales[area_vocacional]] += 1

    area_maxima = max(areas_puntuacion, key=areas_puntuacion.get)

    ventana_area = tk.Toplevel(root)
    ventana_area.title("Área Vocacional")

    font_defecto = tk_font.nametofont("TkDefaultFont")
    tamano_fuente = font_defecto.cget("size")

    texto_area = tk.Label(ventana_area, text=f"Tu área vocacional predominante es: {area_maxima}", font=(None, int(tamano_fuente * 1.2)))
    texto_area.pack(pady=10)

    boton_cerrar = tk.Button(ventana_area, text="Cerrar", command=cerrar_ventana)
    boton_cerrar.pack(pady=10)

    # Centrar la ventana del área vocacional
    ventana_area.update_idletasks()
    ancho_ventana = ventana_area.winfo_reqwidth()
    alto_ventana = ventana_area.winfo_reqheight()
    x = (root.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y = (root.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana_area.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    ventana_area.focus_force()
    ventana_area.grab_set()
    root.after(5000, cerrar_ventana)  # Cerrar la ventana después de 5 segundos

# Crear la instancia principal de Tkinter
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal de Tkinter

# Inicializar los bloques
bloques = generar_bloques()

# Bucle principal del juego
running = True
while running:
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

        # Teclas presionadas
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                velocidad_personaje_x = -5
            elif evento.key == pygame.K_RIGHT:
                velocidad_personaje_x = 5
            elif evento.key == pygame.K_SPACE and not saltando:
                saltando = True
                velocidad_personaje_y = velocidad_salto

        # Teclas soltadas
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT:
                velocidad_personaje_x = 0

    # Teclas presionadas
    teclas_presionadas = pygame.key.get_pressed()
    if teclas_presionadas[pygame.K_LEFT]:
        velocidad_personaje_x = -5
    elif teclas_presionadas[pygame.K_RIGHT]:
        velocidad_personaje_x = 5
    else:
        velocidad_personaje_x = 0

    # Actualizar la posición del personaje
    if saltando:
        velocidad_personaje_y += gravedad
        personaje_rect.y += velocidad_personaje_y
        if personaje_rect.bottom >= ALTO_PANTALLA:
            personaje_rect.bottom = ALTO_PANTALLA
            saltando = False
            velocidad_personaje_y = 0
    personaje_rect.x += velocidad_personaje_x

    # Colisión con los bordes
    if personaje_rect.left < 0:
        personaje_rect.left = 0
        velocidad_personaje_x = 0
    if personaje_rect.right > ANCHO_PANTALLA:
        personaje_rect.right = ANCHO_PANTALLA
        velocidad_personaje_x = 0
    if personaje_rect.top < 0:
        personaje_rect.top = 0
        velocidad_personaje_y = 0

    # Colisión con los bloques
    bloques_a_eliminar = []
    preguntas_respondidas = []
    for bloque_rect, pregunta in bloques[:]:
        if personaje_rect.colliderect(bloque_rect):
            if personaje_rect.right > bloque_rect.left > personaje_rect.left:  # Colisión por la derecha
                bloques_a_eliminar.append((bloque_rect, pregunta))
                bloques_tocados += 1
                vidas -= 1
                pregunta_actual = None  # Reiniciar la pregunta actual
                preguntas_usadas.append(pregunta)
                preguntas_respondidas.append(pregunta)
                mostrar_pregunta(*pregunta)
            else:  # Colisión por los lados o por abajo
                velocidad_personaje_y = 0

    for bloque_rect, pregunta in bloques_a_eliminar:
        if (bloque_rect, pregunta) in bloques:
            bloques.remove((bloque_rect, pregunta))

    # Generar nuevos bloques si se han respondido todas las preguntas del lote actual
    if not bloques and preguntas_respondidas:
        indice_lote_actual += 1
        if indice_lote_actual < len(lotes_preguntas):
            bloques = generar_bloques()
        else:
            juego_terminado = True

    # Renderizar
    pantalla.blit(fondo, (0, 0))
    for bloque_rect, _ in bloques:
        pantalla.blit(bloque, bloque_rect)
    pantalla.blit(personaje, personaje_rect)
    pygame.display.flip()

    # Mostrar pantalla de "Felicidades" si el juego ha terminado
    if juego_terminado:
        font = pygame.font.Font(None, 48)
        texto_final = font.render("Felicidades! Has completado el juego.", True, NEGRO)
        texto_rect = texto_final.get_rect()
        texto_rect.center = (ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
        pantalla.blit(texto_final, texto_rect)
        pygame.display.flip()
        pygame.time.delay(3000)  # Esperar 3 segundos antes de mostrar el área vocacional

        mostrar_area_vocacional()
        root.mainloop()  # Iniciar el bucle principal de Tkinter

    # Control de FPS
    reloj.tick(FPS)

# Salir de Pygame
pygame.quit()