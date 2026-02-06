from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# --- Textures and Block Types ---
GRASS_TEXTURE = 'grass'
STONE_TEXTURE = 'stone'
BRICK_TEXTURE = 'brick'
DIRT_TEXTURE  = 'dirt'

current_texture = GRASS_TEXTURE

class Voxel(Button):
    def __init__(self, position = (0,0,0), texture = GRASS_TEXTURE):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = 0.5,
            texture = texture,
            color = color.hsv(0, 0, random.uniform(0.9, 1)),
            scale = 0.99
        )

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                Voxel(position = self.position + mouse.normal, texture = current_texture)
            if key == 'right mouse down':
                destroy(self)

# --- World Generation ---
for z in range(20):
    for x in range(20):
        Voxel(position = (x, 0, z))

# --- Player and Environment ---
player = FirstPersonController()
sky = Sky()

# Visual item representing the held block
hand = Entity(
    parent = camera.ui,
    model = 'cube',
    texture = current_texture,
    scale = 0.2,
    rotation = Vec3(150, -10, 0),
    position = Vec3(0.3, -0.6, 2)
)

def update():
    global current_texture
    if held_keys['1']: current_texture = GRASS_TEXTURE
    if held_keys['2']: current_texture = STONE_TEXTURE
    if held_keys['3']: current_texture = BRICK_TEXTURE
    if held_keys['4']: current_texture = DIRT_TEXTURE

    # Update hand visual
    hand.texture = current_texture

    # Hand animation
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.position = Vec3(0.5, -0.5, 2.5)
    else:
        hand.position = Vec3(0.3, -0.6, 2)

app.run()
