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

class Crop:
    def __init__(self, plant_type):
        self.state = 'planted'
        self.plant_time = time.time()  
        self.plant_type = plant_type

    def grow(self):
        if self.state == 'planted':
            elapsed_time = time.time() - self.plant_time
            if elapsed_time >= GROWTH_DURATION:
                self.state = 'ready'
                print(f"A {self.plant_type} has grown!")

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
selected_plant_type = "Plant 1"
inventory_capacity = 30
coins = 100

def toggle_inventory():
    global inventory_visible
    inventory_visible = not inventory_visible

def toggle_shop():
    global shop_visible
    shop_visible = not shop_visible

def select_plant_type(mouse_pos):
    global selected_plant_type
    font = pygame.font.Font(None, 24)
    y_offset = 60
    for plant_type in PLANT_TYPES.keys():
        text_rect = font.render(f"{plant_type}: {PLANT_TYPES[plant_type]['quantity']}", True, (255, 255, 255)).get_rect()
        text_rect.topleft = (810, y_offset)
        if text_rect.collidepoint(mouse_pos):
            selected_plant_type = plant_type
            print(f"Selected plant type: {selected_plant_type}")
            break
        y_offset += 30

def plant_crop(grid_x, grid_y):
    global selected_plant_type
    if PLANT_TYPES[selected_plant_type]["quantity"] > 0:
        crops[grid_x][grid_y] = Crop(selected_plant_type)
        PLANT_TYPES[selected_plant_type]["quantity"] -= 1
        print(f"Planted {selected_plant_type} at ({grid_x}, {grid_y})")

def collect_crop(x, y):
    if crops[x][y] and crops[x][y].state == 'ready':
        plant_type = crops[x][y].plant_type
        PLANT_TYPES[plant_type]["quantity"] += 2  
        print(f"Collected a {plant_type} at ({x}, {y})")
        crops[x][y] = None  

def buy_plant(plant_type):
    global coins
    if coins >= PLANT_TYPES[plant_type]["price"]:
        PLANT_TYPES[plant_type]["quantity"] += 1
        coins -= PLANT_TYPES[plant_type]["price"]
        print(f"Bought 1 unit of {plant_type} for {PLANT_TYPES[plant_type]['price']} coins.")

def sell_plant(plant_type):
    global coins
    if PLANT_TYPES[plant_type]["quantity"] > 0:
        PLANT_TYPES[plant_type]["quantity"] -= 1
        coins += PLANT_TYPES[plant_type]["price"]
        print(f"Sold 1 unit of {plant_type} for {PLANT_TYPES[plant_type]['price']} coins.")

def expand_inventory():
    global inventory_capacity, coins
    expansion_cost = 50
    if coins >= expansion_cost:
        inventory_capacity += 10
        coins -= expansion_cost
        print("Inventory expanded by 10 slots.")

def main():
    global coins
    running = True
    highlighted_tile = None

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x, grid_y = screen_to_iso(mouse_x, mouse_y)

        if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
            highlighted_tile = (grid_x, grid_y)
        else:
            highlighted_tile = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    toggle_inventory()
                if event.key == pygame.K_t:
                    toggle_shop()

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    if inventory_visible:
                        select_plant_type(event.pos)
                    elif shop_visible:
                        handle_shop_click(event.pos)
                    elif highlighted_tile and PLANT_TYPES[selected_plant_type]["quantity"] > 0:
                        plant_crop(grid_x, grid_y)
                elif event.button == 3:  # Right click
                    if highlighted_tile:
                        collect_crop(grid_x, grid_y)

        for x in range(grid_width):
            for y in range(grid_height):
                if crops[x][y] is not None:
                    crops[x][y].grow()

        screen.fill((0, 0, 0))  

        scaled_tile_width = tile_width * scale_factor
        scaled_tile_height = tile_height * scale_factor

        for x in range(grid_width):
            for y in range(grid_height):
                screen_x, screen_y = iso_to_screen(x, y)
                color = COLOR_EMPTY

                if crops[x][y] is not None:
                    if crops[x][y].state == 'planted':
                        color = PLANT_TYPES[crops[x][y].plant_type]["color"]
                    elif crops[x][y].state == 'ready':
                        color = COLOR_READY

                    pygame.draw.circle(screen, (255, 0, 0), (screen_x + scaled_tile_width // 2, screen_y + scaled_tile_height // 2), 3)

                pygame.draw.polygon(screen, color,
                                    [(screen_x + scaled_tile_width // 2, screen_y),
                                     (screen_x + scaled_tile_width, screen_y + scaled_tile_height // 2),
                                     (screen_x + scaled_tile_width // 2, screen_y + scaled_tile_height),
                                     (screen_x, screen_y + scaled_tile_height // 2)])

        if highlighted_tile:
            screen_x, screen_y = iso_to_screen(highlighted_tile[0], highlighted_tile[1])
            pygame.draw.polygon(screen, COLOR_HIGHLIGHT,
                                [(screen_x + scaled_tile_width // 2, screen_y),
                                 (screen_x + scaled_tile_width, screen_y + scaled_tile_height // 2),
                                 (screen_x + scaled_tile_width // 2, screen_y + scaled_tile_height),
                                 (screen_x, screen_y + scaled_tile_height // 2)], 2)

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

        pygame.display.flip()

    pygame.quit()

main()
