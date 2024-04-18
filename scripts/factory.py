

import pygame

from scripts.enemy import Enemy


class Factory:

  def create_leaf_spawner(self, tile_list):
    leaf_spawners = []

    for tree in tile_list:
      leaf_spawners.append(
        pygame.Rect(
          tree['pos'][0],
          tree['pos'][1],
          20, 15
        )
      )
    return leaf_spawners
  
  def create_character_spawner(self, game_instance, player, spawn_list):
    enemy_spawners = []
    
    for spawner in spawn_list:
      #player
      if spawner['variant'] == 0:
        player.pos = spawner['pos']
        player.air_time = 0
      #enemy
      else:
        enemy_spawners.append(Enemy(game_instance, spawner['pos'], (8, 15)))
    return enemy_spawners