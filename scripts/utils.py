import os

import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path, colorkey=(0, 0, 0)):
    img = None
    if colorkey is not None:
      img = pygame.image.load(BASE_IMG_PATH + path).convert()
      img.set_colorkey((0, 0, 0))
    else:
      img = pygame.image.load(BASE_IMG_PATH + path).convert_alpha()

    return img

def load_images(path, colorkey=(0, 0, 0)):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name, colorkey))
    return images

def create_outline(non_silhouette_surf, display_surf):
  #Select a surface for masking
  mask = pygame.mask.from_surface(display_surf)
  #All non-transparent color becomes black
  #according to setcolor All transparent color becomes 
  #transparent according to unsetcolor.
  #remember, to_surface creates a copy of the surface from 'from_surface',
  #it doesn't modify the surface.
  silhouette = mask.to_surface(setcolor=(0,0,0,100), unsetcolor=(0,0,0,0))

  for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    non_silhouette_surf.blit(silhouette, offset)

  #Override silhouette
  non_silhouette_surf.blit(display_surf, (0, 0))