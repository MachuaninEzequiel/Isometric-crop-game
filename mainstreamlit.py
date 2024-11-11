import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt

# Configuración de variables y parámetros
tile_width, tile_height = 32, 16
grid_width, grid_height = 10, 10
GROWTH_DURATION = 5  
scale_factor = 2  

PLANT_TYPES = {
    "Plant 1": {"color": (0, 255, 0), "quantity": 10, "rarity": "common", "price": 5},
    "Plant 2": {"color": (0, 0, 255), "quantity": 10, "rarity": "rare", "price": 10},
    "Plant 3": {"color": (255, 0, 0), "quantity": 10, "rarity": "epic", "price": 20}
}

COLOR_EMPTY = (200, 200, 200)
COLOR_READY = (255, 255, 0)

# Clase para representar cultivos
class Crop:
    def __init__(self, plant_type):
        self.state = 'planted'
        self.plant_time = time.time()
        self.plant_type = plant_type

    def grow(self):
        if self.state == 'planted' and time.time() - self.plant_time >= GROWTH_DURATION:
            self.state = 'ready'

# Crear la cuadrícula de cultivos
crops = [[None for _ in range(grid_height)] for _ in range(grid_width)]

# Funciones de conversión de coordenadas
def iso_to_screen(x, y):
    scaled_tile_width = tile_width * scale_factor
    scaled_tile_height = tile_height * scale_factor
    screen_x = (x - y) * (scaled_tile_width // 2) + 500
    screen_y = (x + y) * (scaled_tile_height // 2) + 250
    return screen_x, screen_y

# Función para plantar un cultivo
def plant_crop(grid_x, grid_y, selected_plant_type):
    if PLANT_TYPES[selected_plant_type]["quantity"] > 0:
        crops[grid_x][grid_y] = Crop(selected_plant_type)
        PLANT_TYPES[selected_plant_type]["quantity"] -= 1

# Función para recolectar un cultivo
def collect_crop(x, y):
    if crops[x][y] and crops[x][y].state == 'ready':
        plant_type = crops[x][y].plant_type
        PLANT_TYPES[plant_type]["quantity"] += 2  
        crops[x][y] = None

# Interfaz de Streamlit
st.title("Simulador de Agricultura Isométrico")
selected_plant_type = st.selectbox("Selecciona un tipo de planta", list(PLANT_TYPES.keys()))
if st.button("Plantar"):
    x, y = st.slider("Selecciona X", 0, grid_width - 1), st.slider("Selecciona Y", 0, grid_height - 1)
    plant_crop(x, y, selected_plant_type)

# Dibujar el mapa
fig, ax = plt.subplots()
for x in range(grid_width):
    for y in range(grid_height):
        screen_x, screen_y = iso_to_screen(x, y)
        color = COLOR_EMPTY if crops[x][y] is None else (PLANT_TYPES[crops[x][y].plant_type]["color"] if crops[x][y].state == 'planted' else COLOR_READY)
        rect = plt.Polygon([[screen_x, screen_y], [screen_x + tile_width, screen_y + tile_height // 2],
                            [screen_x, screen_y + tile_height], [screen_x - tile_width, screen_y + tile_height // 2]],
                           color=np.array(color) / 255)
        ax.add_patch(rect)

ax.set_xlim(0, 1000)
ax.set_ylim(0, 800)
ax.set_aspect('equal')
st.pyplot(fig)
