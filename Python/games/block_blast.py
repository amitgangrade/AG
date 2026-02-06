import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 850
GRID_SIZE = 8
CELL_SIZE = 60
GRID_MARGIN = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_TOP = 100

# Colors (Vibrant Neon Theme)
BG_COLOR = (15, 15, 35)
GRID_EMPTY = (30, 30, 50)
SHAPE_COLORS = [
    (255, 50, 50),   # Neon Red
    (50, 255, 50),   # Neon Green
    (50, 100, 255),  # Neon Blue
    (255, 200, 50),  # Neon Gold
    (200, 50, 255),  # Neon Purple
    (50, 255, 255)   # Neon Cyan
]
SHAPE_SHADOW = (40, 40, 60, 100)

# --- Shapes Definitions ---
SHAPE_TEMPLATES = [
    # 1x1
    [(0, 0)],
    # 2x2 Square
    [(0,0), (1,0), (0,1), (1,1)],
    # 3x3 Square
    [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2)],
    # Horizontal lines
    [(0,0), (1,0)],
    [(0,0), (1,0), (2,0)],
    [(0,0), (1,0), (2,0), (3,0)],
    [(0,0), (1,0), (2,0), (3,0), (4,0)],
    # Vertical lines
    [(0,0), (0,1)],
    [(0,0), (0,1), (0,2)],
    [(0,0), (0,1), (0,2), (0,3)],
    # L-shapes
    [(0,0), (0,1), (1,1)],
    [(0,0), (1,0), (0,1), (0,2)],
    # T-shape
    [(0,0), (1,0), (2,0), (1,1)],
    # Z-shape
    [(0,0), (1,0), (1,1), (2,1)],
]

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 1.0  # Normalized life 1.0 -> 0.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05
        return self.life > 0

class Block:
    def __init__(self, color):
        self.color = color
        self.alpha = 255
        self.scale = 1.0
        self.clearing = False

class Shape:
    def __init__(self, template, color_idx):
        self.blocks = template
        self.color = SHAPE_COLORS[color_idx]
        self.color_idx = color_idx
        self.pos = [0, 0]
        self.dragging = False
        self.initial_center = [0, 0]
        self.active = True
        self.scale = 1.0  # For pick-up animation

    def get_width_height(self):
        max_x = max(b[0] for b in self.blocks)
        max_y = max(b[1] for b in self.blocks)
        return (max_x + 1) * CELL_SIZE, (max_y + 1) * CELL_SIZE

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BLOCK BLAST - NEON EDITION")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Inter, Arial Black", 64)
        self.small_font = pygame.font.SysFont("Inter, Arial", 24)
        
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.shapes = []
        self.particles = []
        self.spawn_shapes()
        
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.dragging_shape = None
        self.drag_offset = (0, 0)

    def spawn_shapes(self):
        self.shapes = []
        for i in range(3):
            template = random.choice(SHAPE_TEMPLATES)
            color_idx = random.randint(0, len(SHAPE_COLORS) - 1)
            shape = Shape(template, color_idx)
            w, h = shape.get_width_height()
            spacing = SCREEN_WIDTH // 3
            shape.pos = [spacing * i + (spacing - w) // 2, 650 + (150 - h) // 2]
            shape.initial_center = list(shape.pos)
            self.shapes.append(shape)

    def draw_rounded_rect(self, surface, color, rect, radius=10, alpha=255):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        c = list(color) + [alpha]
        pygame.draw.rect(s, c, (0, 0, rect[2], rect[3]), border_radius=radius)
        # Highlight
        h_color = [min(255, x + 40) for x in color] + [alpha]
        pygame.draw.rect(s, h_color, (0, 0, rect[2], rect[3]), width=2, border_radius=radius)
        surface.blit(s, (rect[0], rect[1]))

    def get_grid_from_pos(self, px, py):
        gx = (px - GRID_MARGIN + CELL_SIZE // 2) // CELL_SIZE
        gy = (py - GRID_TOP + CELL_SIZE // 2) // CELL_SIZE
        return int(gx), int(gy)

    def can_place(self, shape, gx, gy):
        for bx, by in shape.blocks:
            tx, ty = gx + bx, gy + by
            if not (0 <= tx < GRID_SIZE and 0 <= ty < GRID_SIZE):
                return False
            if self.grid[ty][tx] is not None:
                return False
        return True

    def place_shape(self, shape, gx, gy):
        for bx, by in shape.blocks:
            self.grid[gy + by][gx + bx] = Block(shape.color)
        shape.active = False
        self.score += len(shape.blocks) * 10
        self.check_lines()
        
        if all(not s.active for s in self.shapes):
            self.spawn_shapes()
            
        if self.is_game_over():
            self.game_over = True

    def check_lines(self):
        rows_to_clear = []
        cols_to_clear = []
        
        for y in range(GRID_SIZE):
            if all(self.grid[y][x] is not None for x in range(GRID_SIZE)):
                rows_to_clear.append(y)
        for x in range(GRID_SIZE):
            if all(self.grid[y][x] is not None for y in range(GRID_SIZE)):
                cols_to_clear.append(x)
        
        cleared_count = 0
        for y in rows_to_clear:
            for x in range(GRID_SIZE):
                self.create_particles(GRID_MARGIN + x * CELL_SIZE + CELL_SIZE//2, GRID_TOP + y * CELL_SIZE + CELL_SIZE//2, self.grid[y][x].color)
                self.grid[y][x] = None
            cleared_count += 1
        for x in cols_to_clear:
            for y in range(GRID_SIZE):
                if self.grid[y][x]:
                    self.create_particles(GRID_MARGIN + x * CELL_SIZE + CELL_SIZE//2, GRID_TOP + y * CELL_SIZE + CELL_SIZE//2, self.grid[y][x].color)
                    self.grid[y][x] = None
            cleared_count += 1
            
        if cleared_count > 0:
            self.score += (cleared_count ** 2) * 100

    def create_particles(self, x, y, color):
        for _ in range(8):
            self.particles.append(Particle(x, y, color))

    def is_game_over(self):
        for shape in self.shapes:
            if not shape.active: continue
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if self.can_place(shape, x, y):
                        return False
        return True

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.__init__()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for shape in self.shapes:
                    if not shape.active: continue
                    w, h = shape.get_width_height()
                    if shape.pos[0] <= mx <= shape.pos[0] + w and shape.pos[1] <= my <= shape.pos[1] + h:
                        self.dragging_shape = shape
                        self.drag_offset = (shape.pos[0] - mx, shape.pos[1] - my)
                        self.dragging_shape.scale = 1.1 # Scale up on pick
                        break

            if event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_shape:
                    self.dragging_shape.scale = 1.0
                    mx, my = pygame.mouse.get_pos()
                    gx, gy = self.get_grid_from_pos(mx + self.drag_offset[0], my + self.drag_offset[1])
                    if self.can_place(self.dragging_shape, gx, gy):
                        self.place_shape(self.dragging_shape, gx, gy)
                    else:
                        self.dragging_shape.pos = list(self.dragging_shape.initial_center)
                    self.dragging_shape = None

    def update(self):
        if self.dragging_shape:
            mx, my = pygame.mouse.get_pos()
            self.dragging_shape.pos[0] = mx + self.drag_offset[0]
            self.dragging_shape.pos[1] = my + self.drag_offset[1]
        
        self.particles = [p for p in self.particles if p.update()]

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Draw Score with Glow
        score_surf = self.font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 30))
        
        # Draw Grid Background
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rx = GRID_MARGIN + x * CELL_SIZE
                ry = GRID_TOP + y * CELL_SIZE
                self.draw_rounded_rect(self.screen, GRID_EMPTY, (rx + 4, ry + 4, CELL_SIZE - 8, CELL_SIZE - 8))

        # Draw Placed Blocks
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                block = self.grid[y][x]
                if block:
                    rx = GRID_MARGIN + x * CELL_SIZE
                    ry = GRID_TOP + y * CELL_SIZE
                    self.draw_rounded_rect(self.screen, block.color, (rx + 4, ry + 4, CELL_SIZE - 8, CELL_SIZE - 8))

        # Draw Available Shapes
        for shape in self.shapes:
            if not shape.active: continue
            curr_cell_size = int(CELL_SIZE * shape.scale)
            for bx, by in shape.blocks:
                rx = shape.pos[0] + bx * curr_cell_size
                ry = shape.pos[1] + by * curr_cell_size
                
                # Ghost shadow
                if shape == self.dragging_shape:
                    gx, gy = self.get_grid_from_pos(shape.pos[0], shape.pos[1])
                    if 0 <= gx + bx < GRID_SIZE and 0 <= gy + by < GRID_SIZE:
                        grx = GRID_MARGIN + (gx + bx) * CELL_SIZE
                        gry = GRID_TOP + (gy + by) * CELL_SIZE
                        ghost_color = (255, 255, 255, 70) if self.can_place(shape, gx, gy) else (255, 0, 0, 70)
                        pygame.draw.rect(self.screen, ghost_color, (grx + 4, gry + 4, CELL_SIZE - 8, CELL_SIZE - 8), border_radius=10)
                
                self.draw_rounded_rect(self.screen, shape.color, (rx + 2, ry + 2, curr_cell_size - 4, curr_cell_size - 4))

        # Draw Particles
        for p in self.particles:
            p_size = int(8 * p.life)
            p_alpha = int(255 * p.life)
            s = pygame.Surface((p_size*2, p_size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, list(p.color) + [p_alpha], (p_size, p_size), p_size)
            self.screen.blit(s, (p.x - p_size, p.y - p_size))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            go_text = self.font.render("GAME OVER", True, (255, 50, 50))
            restart_text = self.small_font.render("Click to Restart", True, (255, 255, 255))
            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
