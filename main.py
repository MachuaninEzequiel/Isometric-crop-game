import pygame
import time

pygame.init()
screen = pygame.display.set_mode((1000, 800))
tile_width, tile_height = 32, 16
grid_width, grid_height = 10, 10
GROWTH_DURATION = 5  
scale_factor = 2  


tile_image = pygame.image.load('grass_tile.png')  
tile_image = pygame.transform.scale(tile_image, (tile_width * scale_factor, tile_height * scale_factor))

plant_image_small = pygame.image.load('plant_small.png')  
plant_image_small = pygame.transform.scale(plant_image_small, (tile_width * scale_factor, tile_height * scale_factor))

plant_image_grown = pygame.image.load('plant_grown.png')  
plant_image_grown = pygame.transform.scale(plant_image_grown, (tile_width * scale_factor, tile_height * scale_factor))

COLOR_HIGHLIGHT = (150, 150, 150)  


class Crop:
    def __init__(self):
        self.state = 'planted'
        self.plant_time = time.time()  

    def grow(self):
        if self.state == 'planted':
            elapsed_time = time.time() - self.plant_time
            if elapsed_time >= GROWTH_DURATION:
                self.state = 'ready'
                print("A plant has grown!")

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

def main():
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

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    if highlighted_tile:
                        grid_x, grid_y = highlighted_tile
                        if crops[grid_x][grid_y] is None:
                            
                            crops[grid_x][grid_y] = Crop()
                            print(f"Planted a crop at ({grid_x}, {grid_y})")
                        else:
                            print(f"Tile at ({grid_x}, {grid_y}) already has a plant")

        
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

                
                screen.blit(tile_image, (screen_x, screen_y))

                
                if crops[x][y] is not None:
                    if crops[x][y].state == 'planted':
                        screen.blit(plant_image_small, (screen_x, screen_y))
                    elif crops[x][y].state == 'ready':
                        screen.blit(plant_image_grown, (screen_x, screen_y))

        
        if highlighted_tile:
            screen_x, screen_y = iso_to_screen(highlighted_tile[0], highlighted_tile[1])
            pygame.draw.polygon(screen, COLOR_HIGHLIGHT,
                                [(screen_x + scaled_tile_width // 2, screen_y),
                                 (screen_x + scaled_tile_width, screen_y + scaled_tile_height // 2),
                                 (screen_x + scaled_tile_width // 2, screen_y + scaled_tile_height),
                                 (screen_x, screen_y + scaled_tile_height // 2)], 2)

        pygame.display.flip()  

    pygame.quit()

if __name__ == "__main__":
    main()
