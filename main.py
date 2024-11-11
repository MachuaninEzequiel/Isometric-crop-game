import pygame
import time
import random

pygame.init()
screen = pygame.display.set_mode((1000, 800))
tile_width, tile_height = 32, 16
grid_width, grid_height = 10, 10
GROWTH_DURATION = 5  
scale_factor = 2  

COLOR_EMPTY = (200, 200, 200)
COLOR_READY = (255, 255, 0)
COLOR_HIGHLIGHT = (150, 150, 150)

# Definición de colores y rarezas para cada tipo de planta
PLANT_TYPES = {
    "Plant 1": {"color": (0, 255, 0), "quantity": 10, "rarity": "common", "price": 5},
    "Plant 2": {"color": (0, 0, 255), "quantity": 10, "rarity": "rare", "price": 10},
    "Plant 3": {"color": (255, 0, 0), "quantity": 10, "rarity": "epic", "price": 20}
}

RARENESS_COLORS = {
    "common": (180, 180, 180),
    "rare": (120, 120, 255),
    "epic": (255, 120, 120)
}

# Inventario inicial de agua y robots
inventory = {
    "water": 10,
    "robots": 0
}

class Crop:
    def __init__(self, plant_type):
        self.state = 'planted'
        self.plant_time = time.time()
        self.is_watered = False
        self.plant_type = plant_type

    def grow(self):
        if self.state == 'planted' and self.is_watered:
            elapsed_time = time.time() - self.plant_time
            if elapsed_time >= GROWTH_DURATION:
                self.state = 'ready'
                print(f"{self.plant_type} has grown!")

    def water(self):
        if self.state == 'planted' and not self.is_watered:
            self.is_watered = True
            print(f"{self.plant_type} has been watered.")
        elif self.state == 'ready':
            print("Planta ya crecida, no se puede regar.")
        else:
            print("Tile vacío o sin planta.")

class AutoHarvester:
    def __init__(self, grid_x, grid_y, range_radius=1):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.range_radius = range_radius

    def water_and_harvest(self):
        for x in range(self.grid_x - self.range_radius, self.grid_x + self.range_radius + 1):
            for y in range(self.grid_y - self.range_radius, self.grid_y + self.range_radius + 1):
                if 0 <= x < grid_width and 0 <= y < grid_height and crops[x][y]:
                    crop = crops[x][y]
                    if crop.state == 'planted' and not crop.is_watered:
                        crop.water()
                    elif crop.state == 'ready':
                        collect_crop(x, y)

auto_harvesters = []

def place_auto_harvester(grid_x, grid_y):
    global auto_harvesters
    auto_harvester = AutoHarvester(grid_x, grid_y)
    auto_harvesters.append(auto_harvester)
    print(f"AutoHarvester placed at ({grid_x}, {grid_y}).")

def iso_to_screen(x, y):
    scaled_tile_width = tile_width * scale_factor
    scaled_tile_height = tile_height * scale_factor
    screen_width = 1000
    screen_height = 800

    middle_x_offset = screen_width // 2 - (grid_width * scaled_tile_width) // 4
    middle_y_offset = screen_height // 2 - (grid_height * scaled_tile_height) // 4

    screen_x = (x - y) * (scaled_tile_width // 2) + middle_x_offset
    screen_y = (x + y) * (scaled_tile_height // 2) + middle_y_offset
    return screen_x, screen_y

def screen_to_iso(screen_x, screen_y):
    scaled_tile_width = tile_width * scale_factor
    scaled_tile_height = tile_height * scale_factor

    middle_x_offset = 1000 // 2 - (grid_width * scaled_tile_width) // 4
    middle_y_offset = 800 // 2 - (grid_height * scaled_tile_height) // 4

    adjusted_x = screen_x - middle_x_offset
    adjusted_y = screen_y - middle_y_offset

    x = (adjusted_x // (scaled_tile_width // 2) + adjusted_y // (scaled_tile_height // 2)) // 2
    y = (adjusted_y // (scaled_tile_height // 2) - (adjusted_x // (scaled_tile_width // 2))) // 2
    return x, y

crops = [[None for _ in range(grid_height)] for _ in range(grid_width)]
inventory_visible = False
shop_visible = False
selected_item = "Plant 1"
inventory_capacity = 30
coins = 100

def total_plants():
    return sum(data["quantity"] for data in PLANT_TYPES.values())

def toggle_inventory():
    global inventory_visible
    inventory_visible = not inventory_visible

def toggle_shop():
    global shop_visible
    shop_visible = not shop_visible

def select_item(mouse_pos):
    global selected_item
    font = pygame.font.Font(None, 24)
    y_offset = 60
    for item in list(PLANT_TYPES.keys()) + ["water", "robots"]:
        text_rect = font.render(f"{item}: {PLANT_TYPES[item]['quantity'] if item in PLANT_TYPES else inventory[item]}", True, (255, 255, 255)).get_rect()
        text_rect.topleft = (810, y_offset)
        if text_rect.collidepoint(mouse_pos):
            selected_item = item
            print(f"Selected item: {selected_item}")
            break
        y_offset += 30

def plant_crop(grid_x, grid_y):
    global selected_item
    if selected_item in PLANT_TYPES and PLANT_TYPES[selected_item]["quantity"] > 0:
        crops[grid_x][grid_y] = Crop(selected_item)
        PLANT_TYPES[selected_item]["quantity"] -= 1
        print(f"Planted {selected_item} at ({grid_x}, {grid_y})")
    elif selected_item == "robots" and inventory["robots"] > 0:
        place_auto_harvester(grid_x, grid_y)
        inventory["robots"] -= 1
    elif selected_item == "water" and inventory["water"] > 0:
        if crops[grid_x][grid_y]:
            crops[grid_x][grid_y].water()
            inventory["water"] -= 1
        else:
            print("No se puede regar, tile sin planta.")

def collect_crop(x, y):
    if crops[x][y] and crops[x][y].state == 'ready':
        plant_type = crops[x][y].plant_type
        if total_plants() < inventory_capacity:
            PLANT_TYPES[plant_type]["quantity"] += 2  
            print(f"Collected a {plant_type} at ({x}, {y})")
            crops[x][y] = None  
        else:
            print("Inventory full! Cannot collect more.") 


def sell_plant(plant_type):
    global coins
    if PLANT_TYPES[plant_type]["quantity"] > 0:
        PLANT_TYPES[plant_type]["quantity"] -= 1
        coins += PLANT_TYPES[plant_type]["price"]
        print(f"Sold 1 unit of {plant_type} for {PLANT_TYPES[plant_type]['price']} coins.")

def buy_item(item):
    global coins
    if item in PLANT_TYPES and total_plants() < inventory_capacity:
        if coins >= PLANT_TYPES[item]["price"]:
            PLANT_TYPES[item]["quantity"] += 1
            coins -= PLANT_TYPES[item]["price"]
            print(f"Bought 1 unit of {item} for {PLANT_TYPES[item]['price']} coins.")
        else:
            print("Not enough coins.")
    elif item == "water" and coins >= 2:
        inventory["water"] += 5
        coins -= 2
        print("Bought 5 units of water for 2 coins.")
    elif item == "robots" and coins >= 20:
        inventory["robots"] += 1
        coins -= 20
        print("Bought 1 AutoHarvester for 20 coins.")
    else:
        print("Inventory full! Cannot buy more.")

def main():
    global coins
    running = True
    highlighted_tile = None

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = screen_to_iso(mouse_x, mouse_y)

        for auto_harvester in auto_harvesters:
            auto_harvester.water_and_harvest()

        if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
            highlighted_tile = (grid_x, grid_y)
        else:
            highlighted_tile = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    toggle_inventory()
                elif event.key == pygame.K_s:
                    toggle_shop()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if inventory_visible:
                        select_item((mouse_x, mouse_y))
                    elif shop_visible:
                        buy_item(selected_item)
                        sell_plant(selected_item)
                    elif highlighted_tile:
                        plant_crop(grid_x, grid_y)
                elif event.button == 3:  # Right click
                    if highlighted_tile:
                        collect_crop(grid_x, grid_y)

        for x in range(grid_width):
            for y in range(grid_height):
                if crops[x][y]:
                    crops[x][y].grow()

        screen.fill((0, 0, 0))
        
        for x in range(grid_width):
            for y in range(grid_height):
                screen_x, screen_y = iso_to_screen(x, y)
                if highlighted_tile == (x, y):
                    color = COLOR_HIGHLIGHT
                elif crops[x][y]:
                    if crops[x][y].state == 'ready':
                        color = COLOR_READY
                    else:
                        color = PLANT_TYPES[crops[x][y].plant_type]["color"]
                else:
                    color = COLOR_EMPTY
                pygame.draw.polygon(screen, color, [(screen_x, screen_y), (screen_x + tile_width, screen_y + tile_height // 2),
                                                    (screen_x, screen_y + tile_height), (screen_x - tile_width, screen_y + tile_height // 2)])

        font = pygame.font.Font(None, 24)
        if inventory_visible:
            pygame.draw.rect(screen, (50, 50, 50), (800, 50, 180, 200))
            font = pygame.font.Font(None, 24)
            y_offset = 60
            for plant_type, data in PLANT_TYPES.items():
                color = RARENESS_COLORS[data["rarity"]]
                text = font.render(f"{plant_type} (x{data['quantity']})", True, color)
                screen.blit(text, (810, y_offset))
                y_offset += 30
            text = font.render(f"Coins: {coins}", True, (255, 255, 0))
            screen.blit(text, (810, y_offset + 20))
            text = font.render(f"Capacity: {inventory_capacity}", True, (255, 255, 0))
            screen.blit(text, (810, y_offset + 40))
            text = font.render(f"Water: {inventory['water']}",True, (255, 255, 0))
            screen.blit(text, (810, y_offset + 60))
            text = font.render(f"Robots: {inventory['robots']}",True, (255, 255, 0))
            screen.blit(text, (810, y_offset + 80))

        if shop_visible:
            pygame.draw.rect(screen, (70, 70, 70), (800, 50, 180, 300))
            font = pygame.font.Font(None, 24)
            y_offset = 60
            for plant_type, data in PLANT_TYPES.items():
                text = font.render(f"Buy {plant_type}: {data['price']} coins", True, (255, 255, 255))
                screen.blit(text, (810, y_offset))
                y_offset += 30
            y_offset += 10
            for plant_type, data in PLANT_TYPES.items():
                text = font.render(f"Sell {plant_type}: {data['price']} coins", True, (200, 200, 200))
                screen.blit(text, (810, y_offset))
                y_offset += 30
            text = font.render(f"Inventory+: 50 coins", True, (0, 255, 0))
            screen.blit(text, (810, y_offset + 20))
            #text = font.render(f"Water: {inventory['water']}",True, (255, 255, 0))
            #screen.blit(font.render(text, (810, y_offset + 30), (255, 255, 255)))
            #text = font.render(f"Robots: {inventory['robots']}",True, (255, 255, 0))
            #screen.blit(font.render(text, (810, y_offset + 40), (255, 255, 255)))

        pygame.display.flip()

main()
pygame.quit()
