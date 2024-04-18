import pygame

from scripts.editor.saveload import SaveLoad

CLOSEST_TILES = [
  (-1, 0), #left
  (-1, -1), #top-left
  (0, -1), #top
  (1, -1), #top-right
  (1, 0), #right
  (0, 0), #center
  (-1, 1), #bottom-left
  (0, 1), #bottom
  (1, 1) #bottom-right
]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.saveload = SaveLoad()
        self.game = game
        self.tile_size = tile_size
        #Foreground Tiles that are included in grid system.
        #these tiles have collision box that can collide with
        #players or other objects.
        self.tilemap = {}
        #Background Tiles. These tiles are excluded in 
        #grid system. These tiles consist of decorations and 
        #they don't have collision box.
        self.offgrid_tiles = []

    def extract(self, attr_pairs, keep=False):
      matches = []
      #We use copy() in this function because we don't want
      #the original tiles to be modified 
      #
      #Loop through off-grid tiles
      for tile in self.offgrid_tiles.copy():
        #Check if the selected tile has the same type
        #and variant as the attr_pairs
        if (tile['type'], tile['variant']) in attr_pairs:
          #If true, add a selected tile copy to 'matches' list
          matches.append(tile.copy())
          #if keep is False remove the selected tile to
          #the off-grid tiles list
          if not keep:
            self.offgrid_tiles.remove(tile)

      #Next, loop through on-grid tilemaps
      for loc in self.tilemap:
        tile = self.tilemap[loc]
        #Check if the selected tile has the same type
        #and variant as the attr_pairs
        if (tile['type'], tile['variant']) in attr_pairs:
          #If true, add a selected tile copy to 'matches' list
          matches.append(tile.copy())
          
          #Convert the selected tile copy's x and y
          #to screen coordinates. -1 means the last
          #element in the list which is the newly
          #added tile.
          matches[-1]['pos'][0] *= self.tile_size
          matches[-1]['pos'][1] *= self.tile_size

          if not keep:
            del self.tilemap[loc]
            
      return matches

    #Check if there's a solid tile existing in a
    #specific coordinate
    def solid_tile(self, pos):
      #Get grid coodinate
      tile_loc = str(
          int(pos[0] // self.tile_size)) \
          + ',' + \
          str(int(pos[1] // self.tile_size)
      )
      #Check if grid coordinate has tile in tilemap
      if tile_loc in self.tilemap:
        #Check if the tilemap type has collision box
        if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
          #Return
          return self.tilemap[tile_loc]

    def tiles_around(self, pos):
        tiles = []
        # '//' operator is floor division. the operator doesn't convert
        # its quotient to int that's why we convert it explicitly.
        #closest tiles collision boxes is based on player position.
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in CLOSEST_TILES:
            loc = str(tile_loc[0] + offset[0]) + ',' + str(tile_loc[1] + offset[1])
            if loc in self.tilemap:
                tiles.append(self.tilemap[loc])
        return tiles
    
    def closest_collision_tiles(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def load_map(self, path):
        try:
          map_data = self.saveload.load(path)

          self.tilemap = map_data['tilemap']
          self.tile_size = map_data['tile_size']
          self.offgrid_tiles = map_data['offgrid']
        except FileNotFoundError:
          print("No map found.")

    def render(self, surf, offset):
        for tile in self.offgrid_tiles:
            surf.blit(
              self.game.assets[tile['type']][tile['variant']], 
              (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])
            )
        
        #Map all tiles that's covered by the camera
        #This is more efficient performance-wise rather than
        #rendering all tiles even the ones that are not visible
        #on the screen.
        #
        #First off, convert the top-left(offset[0]) point of the camera to 
        #grid x-coordinate then do the same to the top-right
        #(offset[0] + surf.get_width()) of the camera.
        #Do the same for y-axis to get the top and bottom points of camera.
        #Don't forget to add +1 to the second parameter of range() this is because
        #the second parameter of range is exclusive. In other words, range skips
        #the value in the second param. For example, range(1, 5) will be iterated 
        #from 1 to 4, excluding 5.
        for x in range(int(offset[0] // self.tile_size), int((offset[0] + surf.get_width()) // self.tile_size + 1)):
            for y in range(int(offset[1] // self.tile_size), int((offset[1] + surf.get_height()) // self.tile_size + 1)):
                loc = str(x) + ',' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(
                      self.game.assets[tile['type']][tile['variant']], 
                      (tile['pos'][0] * self.tile_size - offset[0], 
                       tile['pos'][1] * self.tile_size - offset[1])
                    )