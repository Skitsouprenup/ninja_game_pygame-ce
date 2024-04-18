import sys

import pygame

from scripts.editor.saveload import SaveLoad
from scripts.utils import load_images
from scripts.tilemap import Tilemap

from scripts.constants import MAX_LEVEL

#The purpose of this dict is to look for 
#existing closest tile of a tile and fill up
#the tile. Sort the coordinates because this will
#be compared to sorted coordinates in autotile()
#function. We sort coordinates to make sure that
#we always match the same pattern even the coordinates
#of closest tiles in autotile() got shuffled.
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

AUTOTILE_TYPES = {'grass', 'stone'}

#For some reason, the screen-to-grid mapping 
#we have here is failing the higher the mouse
#x and y coordinate. One possible reason for this
#is that we scale the display. What i'm sure about
#is that the grid coordinate is doubled everytime 
#floor division is performed. To fix this, we divide
#mouse x and y by 2 or multiply by '0.5'. It's better
#to use multiplication because it's much faster than
#division
RENDER_SCALE = 0.5

class LevelEditor:
    def __init__(self):
        pygame.init()

        self.argv = sys.argv

        self.editor_mode = 'create'

        pygame.display.set_caption('level editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        
        self.saveload = SaveLoad()

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False, False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawner': load_images('tiles/spawners'),
        }
        self.tilemap = Tilemap(self, tile_size=16)

        self.scroll = [0, 0]

        #when list() method is applied to dictionaries,
        #the keys that will be included in the list
        #and values are excluded
        self.tile_list = list(self.assets)
        #Index of the current selected tile set
        #in tile_list
        self.tile_set = 0
        #Index of the current selected tile variant
        #in the current selected tile set in
        #tile_list
        self.tile_variant = 0

        self.left_click = False
        self.right_click = False
        self.lshift = False
        self.ongrid = True
        self.character_tile = False

        #Load Level
        try:

          map_data = {}

          #argv[0] is the first command-line argument which
          #is the filename of the script being executed
          if len(self.argv) > 2:
            if self.argv[1] == 'edit':
              self.editor_mode = 'edit'
              map_data = self.saveload.load('data/maps/'+self.argv[2]+'.json')

          if len(map_data) > 0:
            self.tilemap.tilemap = map_data['tilemap']
            self.tilemap.tile_size = map_data['tile_size']
            self.tilemap.offgrid_tiles = map_data['offgrid']
        except FileNotFoundError:
          print("No map found. You should create one.")

    def autotile(self):
        #Loop through tiles in the on-grid tilemap.
        #tilemap is a dict and thus, we will be
        #looping through keys not values
        for loc in self.tilemap.tilemap:
          #Get the value corresponds with the key
          selected_tile = self.tilemap.tilemap[loc]
          #initialize a set
          neighbors = tuple()
        
          #Loop through tiles around the selected tile
          for neighbor_coords in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
              #Get the grid coordinates of closest tile
              neighbor_tile = str(selected_tile['pos'][0] + neighbor_coords[0]) + ',' + str(selected_tile['pos'][1] + neighbor_coords[1])
              #Check if there's tile in the closest tile coordinates
              if neighbor_tile in self.tilemap.tilemap:
                  #If closest tile exists, check if the selected tile and the
                  #closest tile has the same type.
                  if self.tilemap.tilemap[neighbor_tile]['type'] == selected_tile['type']:
                      #If both tiles have equal type, add the closest tile to
                      #'neighbors' set
                      neighbors = (*neighbors, neighbor_coords)

          #Sorted convert neighbors to list. Thus, we need to convert it back to tuple
          neighbors = tuple(sorted(neighbors))
          #If the selected tile type is in AUTOTILE_TYPES and a set of closest tiles coords
          #has a match to one of the sets of tiles coords in AUTOTILE_MAP, selected tile
          #will change its variant based on the value of the matched closest tile key
          #in AUTOTILE_MAP.
          #
          #For example, if the closest tiles are top(0, 1) and right(1, 0), if this
          #set of coordinates is registered in AUTOTILE_MAP, selected tile will use
          #the corresponding variant value of the coordiantes set.
          #
          #The syntax '(neighbors in AUTOTILE_MAP)' compares the tuples of AUTOTILE_MAP
          #and 'neighbors'. If the tuples in 'neighbors' are equal to one of the set of
          #tuples in AUTOTILE_MAP, this will be executed.
          if (selected_tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
              selected_tile['variant'] = AUTOTILE_MAP[neighbors]

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            #Add camera offset to every tile position because the camera
            #is a 'moving screen' and we must place tiles relative to
            #the camera.
            #left and right camera movement
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            #top and bottom camera movement
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            int_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #Current selected tile image
            current_tile_img = \
              self.assets[self.tile_list[self.tile_set]][self.tile_variant].copy()
            #Adds transparency for tile preview
            current_tile_img.set_alpha(100)

            self.tilemap.render(self.display, int_scroll)

            self.display.blit(current_tile_img, (5, 5))

            #Get mouse position relative to screen
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (
              mouse_pos[0] * RENDER_SCALE,
              mouse_pos[1] * RENDER_SCALE 
            )

            #Use self.scoll here not the int_scroll because we need the 
            #float values in self.scroll in order to have a more accurate
            #computation.
            tile_grid_pos = (
              int((mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size),
              int((mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size)
            )

            #Preview the current selected tile on the screen
            if self.ongrid and not self.character_tile:
                self.display.blit(
                  current_tile_img,
                  (
                    tile_grid_pos[0] * self.tilemap.tile_size - self.scroll[0],
                    tile_grid_pos[1] * self.tilemap.tile_size - self.scroll[1]
                  )
                )
            else: self.display.blit(current_tile_img, mouse_pos)

            #Add on-grid tile
            if self.left_click and self.ongrid and not self.character_tile:
                self.tilemap.tilemap[
                  str(tile_grid_pos[0]) + 
                  ',' + 
                  str(tile_grid_pos[1])
                ] = { 
                  'type': self.tile_list[self.tile_set],
                  'variant': self.tile_variant,
                  'pos': tile_grid_pos
                }
            #Delete Tile
            if self.right_click:
                tile_loc = str(tile_grid_pos[0]) + ',' + str(tile_grid_pos[1])
                if tile_loc in self.tilemap.tilemap:
                  del self.tilemap.tilemap[tile_loc]

                for tile in self.tilemap.offgrid_tiles:
                  tile_img = self.assets[tile['type']][tile['variant']]
                  #Add collision box to the off-grid tile to test
                  #If our mouse is clicking on it. Subtract the camera
                  #offset here because we're looking for placed tile
                  tile_rect = pygame.Rect(
                    tile['pos'][0] - self.scroll[0],
                    tile['pos'][1] - self.scroll[1],
                    tile_img.get_width(),
                    tile_img.get_height()
                  )
                  #If mouse is in off-grid tile while right clicking,
                  #remove the off-grid tile
                  if tile_rect.collidepoint(mouse_pos):
                      self.tilemap.offgrid_tiles.remove(tile)
                      break
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_click = True
                        if not self.ongrid or self.character_tile:
                            self.tilemap.offgrid_tiles.append(
                              { 
                                'type': self.tile_list[self.tile_set],
                                'variant': self.tile_variant,
                                #No need to convert this to grid coordinates
                                #because off-grid tiles are excluded from
                                #on-grid tiles
                                'pos': (
                                  int(mouse_pos[0] + self.scroll[0]),
                                  int(mouse_pos[1] + self.scroll[1])
                                )
                              }
                            )
                    if event.button == 3:
                        self.right_click = True

                    #Choose tile variant in a tile set
                    if self.lshift:
                      if event.button == 4:
                        self.tile_variant = (
                            (self.tile_variant - 1) % 
                            len(self.assets[self.tile_list[self.tile_set]])
                        )
                      if event.button == 5:
                          self.tile_variant = (
                              (self.tile_variant + 1) % 
                              len(self.assets[self.tile_list[self.tile_set]])
                          )
                    #Choose tile set
                    else:
                        #Mouse Wheel Up
                        if event.button == 4:
                          self.tile_variant = 0
                          #In python modulo operator, when one of the
                          #operands is a negative number, distribute law of
                          #modulo is implemented
                          #Example:
                          #-3%7 = (-1*7 + 4) % 7 = (-7%7) + (4%7) = 0 + (4%7) = 4
                          #If the negative left operand is less than the 
                          #right operand we can just add them and get the same result.
                          #Example: -3 + 7 = 4
                          self.tile_set = (self.tile_set - 1) % len(self.tile_list)
                        #Mouse Wheel Down
                        if event.button == 5:
                            self.tile_variant = 0
                            self.tile_set = (self.tile_set + 1) % len(self.tile_list)
                        #If tile is a character, automatically place it on off-grid tile
                        if self.tile_list[self.tile_set] == 'spawner':
                          self.character_tile = True
                        else: self.character_tile = False

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_click = False
                    if event.button == 3:
                        self.right_click = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        if not self.character_tile:
                          self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        file_path = 'data/maps/'+str(MAX_LEVEL)+'.json'

                        if self.editor_mode == 'edit':
                          file_path = 'data/maps/'+self.argv[2]+'.json'

                        #Save Level
                        self.saveload.save(
                          file_path,
                          {
                            'tilemap': self.tilemap.tilemap, 
                            'tile_size': self.tilemap.tile_size, 
                            'offgrid': self.tilemap.offgrid_tiles
                          }
                        )
                    if event.key == pygame.K_t:
                        self.autotile()
                    if event.key == pygame.K_LSHIFT:
                        self.lshift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.lshift = False
            
            self.screen.blit(
              pygame.transform.scale(self.display, self.screen.get_size()), 
              (0, 0)
            )
            pygame.display.update()
            self.clock.tick(60)

LevelEditor().run()
