
import os

import pygame
from scripts.animation import Animation
from scripts.utils import load_image, load_images

#unit used here is number of frames
SCREEN_TRANSITION_DURATION = 30

#List of levels
LEVEL_LIST = os.listdir('data/maps')

#number of levels
MAX_LEVEL = len(LEVEL_LIST)

def init_assets():
  return {
  'decor': load_images('tiles/decor'),
  'grass': load_images('tiles/grass'),
  'large_decor': load_images('tiles/large_decor'),
  'stone': load_images('tiles/stone'),
  'spawner': load_images('tiles/spawners'),
  'player': load_image('entities/player.png', None),
  'background': load_image('background.png'),
  'clouds': load_images('clouds'),
  'gun': load_image('gun.png'),
  'projectile': load_image('projectile.png')
}

def init_anims():
  return {
    'player/idle': Animation(load_images('entities/player/idle', None)),
    'player/run': Animation(load_images('entities/player/run', None), frame_duration=4),
    'player/jump': Animation(load_images('entities/player/jump', None)),
    'player/wall_slide': Animation(load_images('entities/player/wall_slide', None)),
    'particle/leaf': Animation(load_images('particles/leaf'), frame_duration=12, loop=False),
    'particle/dash': Animation(load_images('particles/particle'), frame_duration=6, loop=False),
    'enemy/idle': Animation(load_images('entities/enemy/idle'), frame_duration=6),
    'enemy/run': Animation(load_images('entities/enemy/run'), frame_duration=4)
  }

def init_sfx():
  sounds = {
    'jump': (pygame.mixer.Sound('data/sfx/jump.wav'), 0.7),
    'dash': (pygame.mixer.Sound('data/sfx/dash.wav'), 0.3),
    'hit': (pygame.mixer.Sound('data/sfx/hit.wav'), 0.8),
    'shoot': (pygame.mixer.Sound('data/sfx/shoot.wav'), 0.4),
    'ambience': (pygame.mixer.Sound('data/sfx/ambience.wav'), 0.2)
  }

  for sound in sounds:
    volume = sounds[sound][1]
    sounds[sound][0].set_volume(volume)

  return sounds