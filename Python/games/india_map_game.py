import pygame
import sys
import threading
import requests
import math
import json
import os
from cities_data import INDIA_CITIES

# Constants
WIDTH, HEIGHT = 900, 1000
FPS = 60
BG_COLOR = (173, 216, 230)
TEXT_COLOR = (0, 0, 0)
HOVER_COLOR = (255, 0, 0)
DOT_COLOR = (0, 0, 128)

# Reference cities for calibration (Must be in cities_data)
REF_CITY_1 = "Delhi"
REF_CITY_2 = "Bangalore"

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("India Map Explorer - Guess the City!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.title_font = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.info_font = pygame.font.SysFont("Segoe UI", 14)
        
        self.cities = INDIA_CITIES
        self.hovered_city = None
        self.weather_cache = {}
        self.wiki_cache = {}
        self.loading_data = False
        self.debug_mode = False
        
        # Load Map
        try:
            self.map_img = pygame.image.load("india_map.png")
            # Keep aspect ratio
            img_rect = self.map_img.get_rect()
            scale = min((WIDTH - 50) / img_rect.width, (HEIGHT - 100) / img_rect.height)
            new_size = (int(img_rect.width * scale), int(img_rect.height * scale))
            self.map_img = pygame.transform.scale(self.map_img, new_size)
            self.map_x = (WIDTH - new_size[0]) // 2
            self.map_y = (HEIGHT - new_size[1]) // 2 + 50
            self.use_image = True
        except:
            self.use_image = False
            self.map_x, self.map_y = 50, 50

        # Calibration State
        self.calibration_file = "calibration.json"
        self.calibration_step = 0 # 0: None, 1: Click City 1, 2: Click City 2
        self.calib_points = [] # [(screen_x, screen_y), ...]
        self.proj_params = None # {scale_x, off_x, scale_y, off_y}
        
        self.load_calibration()
        
    def load_calibration(self):
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    self.proj_params = json.load(f)
                self.calibration_step = 0
            except:
                self.start_calibration()
        else:
            self.start_calibration()

    def start_calibration(self):
        print("Starting Calibration...")
        self.calibration_step = 1
        self.calib_points = []
        self.proj_params = None

    def handle_click(self, pos):
        if self.calibration_step == 1:
            self.calib_points.append(pos)
            self.calibration_step = 2
        elif self.calibration_step == 2:
            self.calib_points.append(pos)
            self.solve_calibration()
            self.calibration_step = 0

    def solve_calibration(self):
        # We have Screen (x,y) for two points.
        # We have Lat/Lon for two points.
        # We solve for linear mapping: Screen = Scale * Geo + Offset
        
        p1_screen = self.calib_points[0]
        p2_screen = self.calib_points[1]
        
        c1 = next(c for c in self.cities if c["name"] == REF_CITY_1)
        c2 = next(c for c in self.cities if c["name"] == REF_CITY_2)
        
        # X Axis (Longitude)
        # x1 = m * lon1 + c
        # x2 = m * lon2 + c
        # m = (x1 - x2) / (lon1 - lon2)
        scale_x = (p1_screen[0] - p2_screen[0]) / (c1["lon"] - c2["lon"])
        off_x = p1_screen[0] - (scale_x * c1["lon"])
        
        # Y Axis (Latitude)
        scale_y = (p1_screen[1] - p2_screen[1]) / (c1["lat"] - c2["lat"])
        off_y = p1_screen[1] - (scale_y * c1["lat"])
        
        self.proj_params = {
            "scale_x": scale_x, "off_x": off_x,
            "scale_y": scale_y, "off_y": off_y
        }
        
        with open(self.calibration_file, 'w') as f:
            json.dump(self.proj_params, f)
            
        print("Calibration Saved!")

    def project(self, lat, lon):
        if self.proj_params:
            x = (self.proj_params["scale_x"] * lon) + self.proj_params["off_x"]
            y = (self.proj_params["scale_y"] * lat) + self.proj_params["off_y"]
            return int(x), int(y)
        
        # Fallback (Should not happen unless calibration cancelled)
        return 0, 0

    def fetch_data(self, city):
        name = city["name"]
        if name in self.weather_cache: return # Optimization
            
        self.loading_data = True
        try:
            if name not in self.weather_cache:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true"
                res = requests.get(url, timeout=2)
                if res.status_code == 200:
                    self.weather_cache[name] = f"{res.json()['current_weather']['temperature']} C"
                    
            if name not in self.wiki_cache:
                wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
                headers = {'User-Agent': 'IndiaMapGame/1.0'}
                res = requests.get(wiki_url, headers=headers, timeout=2)
                if res.status_code == 200:
                     self.wiki_cache[name] = res.json().get("extract", "")[:200] + "..."
        except:
            pass
        finally:
            self.loading_data = False

    def check_hover(self, mouse_pos):
        if self.calibration_step > 0: return

        mx, my = mouse_pos
        self.hovered_city = None
        for city in self.cities:
            cx, cy = self.project(city["lat"], city["lon"])
            if math.hypot(cx - mx, cy - my) < 8:
                self.hovered_city = city
                threading.Thread(target=self.fetch_data, args=(city,), daemon=True).start()
                break

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        # Map
        if self.use_image:
            self.screen.blit(self.map_img, (self.map_x, self.map_y))
        else:
             text = self.title_font.render("No Map Image", True, (0,0,0))
             self.screen.blit(text, (WIDTH//2, HEIGHT//2))

        # Title
        title_text = "India Explorer"
        if self.calibration_step == 1: title_text = f"CALIBRATION: Click exactly on {REF_CITY_1}"
        if self.calibration_step == 2: title_text = f"CALIBRATION: Click exactly on {REF_CITY_2}"
        
        t_surf = self.title_font.render(title_text, True, (0,0,50) if self.calibration_step == 0 else (200, 0, 0))
        self.screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 10))

        # Draw Dots (Only in Game Mode)
        if self.calibration_step == 0:
            for city in self.cities:
                cx, cy = self.project(city["lat"], city["lon"])
                color = HOVER_COLOR if self.hovered_city == city else DOT_COLOR
                size = 9 if self.hovered_city == city else 5
                pygame.draw.circle(self.screen, color, (cx, cy), size)
            
            # Show tooltip
            if self.hovered_city:
                self.draw_tooltip()
                
            # Re-Calibrate Help
            help_text = self.info_font.render("Press 'R' to Re-Calibrate Map", True, (100, 100, 100))
            self.screen.blit(help_text, (10, HEIGHT - 30))

        pygame.display.flip()

    def draw_tooltip(self):
        city = self.hovered_city
        weather = self.weather_cache.get(city["name"], "...")
        wiki = self.wiki_cache.get(city["name"], "")
        
        lines = [
            f"{city['name']}",
            f"Weather: {weather}",
            f"Facts: {city.get('facts', '')}",
        ]
        
        # Simple Box Drawing
        x, y = pygame.mouse.get_pos()
        x += 15; y += 15
        
        # Draw Code similar to before...
        # (Simplified for brevity in this massive replace block, logic remains same)
        rect = pygame.Rect(x, y, 300, 100 + (50 if wiki else 0))
        if rect.right > WIDTH: rect.x -= 320
        pygame.draw.rect(self.screen, (255,255,255), rect, border_radius=8)
        pygame.draw.rect(self.screen, (0,0,0), rect, 2, border_radius=8)
        
        curr_y = rect.y + 10
        for line in lines:
            s = self.info_font.render(line, True, (0,0,0))
            self.screen.blit(s, (rect.x+10, curr_y))
            curr_y += 20
        
        if wiki:
            s = self.info_font.render(f"Wiki: {wiki[:40]}...", True, (50,50,50))
            self.screen.blit(s, (rect.x+10, curr_y))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and self.calibration_step > 0:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.check_hover(event.pos)
                elif event.type == pygame.KEYDOWN:
                     if event.key == pygame.K_r:
                         self.start_calibration()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
