
import math
import random

import pygame
from scripts.entities import PhysicsEntity


class Enemy(PhysicsEntity):
  def __init__(self, game, pos, size):
    super().__init__(game, 'enemy', pos, size)
    self.walking = 0
    #60 = 1sec because our framerate is 60FPS
    self.fire_rate = 60
    self.fire_time = 0

  def update(self, tilemap, movement=(0,0)):
    if self.walking:
      #Check if there's a tile on bottom-left or
      #bottom-right of the enemy. We use 6 as offset
      #because I think it's enough to determine the
      #tile. If you change your tile size or enemy size,
      #you should adjust your offsets too.
      if tilemap.solid_tile(
        (
          self.rect().centerx + (-6 if self.flip else 6),
          (self.pos[1] + self.rect().height) + 6
        )
      ):
        #If we already bumped into a left or right wall.
        if (self.collisions['right'] or self.collisions['left']):
          self.flip = not self.flip
        else:
          #if self.flip, move left else, move right
          movement = (-0.5 if self.flip else 0.5, movement[1])
      else:
        self.flip = not self.flip
      
      self.walking = max(0, self.walking - 1)
    #If not walking, set a random movement if
    #the condition here is met which has 1%
    #of happening per frame.
    elif random.random() < 0.01:
      self.walking = random.randint(25, 110)

    if not self.walking:
      dist = (
        self.game.player.pos[0] - self.pos[0],
        self.game.player.pos[1] - self.pos[1]
      )

      #Enemy and player height is 15. so, if
      #their 'y'(top-left point) distance is 
      #less than 12, they're very likely on 
      #their line of sight
      if abs(dist[1]) < 12:
        #If enemy is facing the player at right.
        #distance will be negative if enemy
        #is on the right and player is on the
        #left.
        if self.flip and dist[0] < 0:
          #Shoot the player
          if(self.fire_time == 0):
            self.game.sfx['shoot'][0].play(0)
            self.game.projectiles.append([
              [self.rect().centerx - 2, self.rect().centery],
              -1.25,
              0
            ])
            self.game.create_sparks(
              6,
              #newly added projectile
              self.game.projectiles[-1][0],
              #from -0.25 to 0.75 + math.pi(180 degrees)
              random.random() - 0.25 + math.pi,
              1 + random.random()
            )

        #If enemy is facing the player at left.
        if not self.flip and dist[0] > 0:
          #Shoot the player
          if(self.fire_time == 0):
            self.game.sfx['shoot'][0].play(0)
            self.game.projectiles.append([
              [self.rect().centerx + 2, self.rect().centery],
              1.25,
              0
            ])
            self.game.create_sparks(
              6,
              #newly added projectile
              self.game.projectiles[-1][0],
              random.random() - 0.25,
              1 + random.random()
            )

        self.fire_time += 1
        #timer
        self.fire_time = self.fire_time % self.fire_rate

    if movement[0] != 0:
      self.set_action('run')
    else:
      self.set_action('idle')

    super().update(tilemap, movement)

    #If player is dashing(burst)
    if abs(self.game.player.dashing) >= 50:
      #If enemy and player collide at this point.
      #Enemy is dead.
      if(self.rect().colliderect(self.game.player.rect())):
        self.game.sfx['hit'][0].play(0)
        self.game.explode_entity(30, self.rect().center, self.rect().center)
        self.game.screenshake = max(12, self.game.screenshake)
        return True

  #offset is the camera x and y coordinates
  def render(self, surf, offset):
    super().render(surf, offset)
    #number 2 is just an arbitrary offset.
    #you can change it if you wanna adjust
    #the 'x' position of your gun
    posx_flip = self.rect().centerx - \
    self.game.assets['gun'].get_width() - \
    2 - offset[0]

    if self.flip:
      surf.blit(
        pygame.transform.flip(
          self.game.assets['gun'], 
          self.flip, 
          False
        ),
        (
          posx_flip, 
          self.rect().centery - offset[1]
        )
      )
    else:
      surf.blit(
        self.game.assets['gun'], 
        (
          self.rect().centerx + 2 - offset[0],
          self.rect().centery - offset[1]
        )
      )