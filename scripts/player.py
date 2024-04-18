
import math
import random

from scripts.entities import PhysicsEntity
from scripts.particle import Particle


class Player(PhysicsEntity):
  def __init__(self, game, pos, size):
    super().__init__(game, 'player', pos, size)
    self.air_time = 0
    self.jumps = 1
    self.wall_slide = False
    self.dashing = 0

    self.prev_movement = [0, 0]

  def render(self, surf, non_silhouette, offset):
    if abs(self.dashing) <= 50:
      super().render(surf, offset, non_silhouette)


  def update(self, tilemap, movement):
    super().update(tilemap, movement)
    self.air_time += 1

    self.prev_movement = movement

    if self.air_time >= 180 and not self.wall_slide:
      self.game.dead = 1

    #reset wall slide
    self.wall_slide = False

    #Activate wall slide if the conditions are met
    #Conditions:
    #Player is colliding in left or right walls and
    #air time is greater than 5
    if(self.collisions['right'] or self.collisions['left']) and self.air_time > 5:
      self.wall_slide = True
      self.velocity[1] = min(self.velocity[1], 0.5)
      
      if self.collisions['right']:
        self.flip = False
      else: self.flip = True

      self.set_action('wall_slide')

    if not self.wall_slide:
      # if player is on the ground
      if self.collisions['down']:
        self.air_time = 0
        self.jumps = 1
      #If player is not on the ground for
      #at least 5 frames, player is 
      #considered in jump state
      if self.air_time > 5:
        self.set_action('jump')
      #If player is on the ground and moving left of right
      elif movement[0] != 0:
        self.set_action('run')
      #If player is not in the air and not moving
      #left and right
      else: self.set_action('idle')

    #Wrap the dashing value with abs here because we want
    #this to be implemented in left and right direction.

    #Spawn particles at frame 1(60) and 10(50)
    if abs(self.dashing) in {60, 50}:
      #Spawn 20 particles
      for i in range(20):
        # Get a random angle from a circle(math.pi * 2 or 360 in degrees)
        angle = random.random() * math.pi * 2
        #Get a random speed from 0.25 to 0.75(0.5 + 0.25)
        speed = (random.random() * 0.5) + 0.25
        #random particle velocity based on angle(direction) and speed.
        #Remember that cos and sin functions returns a positive or
        #negative result based on quadrant. For example, 
        #cos(120deg) = ~(-0.5); sin(120) = ~0.86
        #cos() returns the unit length of the vertical part of triangle.
        #Thus, cos() returns y-axis length. sin() returns the unit length
        #of the horizontal part of triangle. Thus, sin() returns x-axis length.
        #You can switch cos() and sin() here if you want. However, the
        #visual effect may change.
        #We use this in order to distribute particles in circular shape.
        p_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.game.particles.append(
          Particle(self.game, 'dash', self.rect().center, p_velocity, random.randint(0, 5))
        )

    #Right Dash
    if self.dashing > 0:
      self.dashing = max(self.dashing -1, 0)
    #Left Dash
    if self.dashing < 0:
      self.dashing = min(0, self.dashing + 1)
    #When dashing initially started.
    #Wrap the dashing value with abs here because we want
    #this to be implemented in left and right direction.
    if abs(self.dashing) > 50:
      #Boost dash for 10 frames. First off, we normalize(unit value)
      #the dash value and multiply it by 7.
      self.velocity[0] = (abs(self.dashing) / self.dashing) * 7
      #Reduce dash for frame 9.
      if abs(self.dashing) == 51:
        self.velocity[0] *= 0.1

      #random x-axis velocity based on the normalized value of dash
      #For example, if the normalized value is a positive value like 0.5 
      #then the player is moving to the right.
      p_velocity = [(abs(self.dashing) / self.dashing) * random.random() * 3, 0]
      self.game.particles.append(
        Particle(self.game, 'dash', self.rect().center, p_velocity, random.randint(0, 5))
      )

    #This acts like a horizontal friction. We do this to
    #reduce horizontal movement especially when player
    #switch state from 'wall_slide' to 'jump' state. 
    if self.velocity[0] > 0:
      self.velocity[0] = max(self.velocity[0] - 0.1, 0)
    else:
      self.velocity[0] = min(self.velocity[0] + 0.1, 0)

  def jump(self):
    if self.wall_slide:
      #Facing left
      if self.flip and self.prev_movement[0] < 0:
        self.velocity[0] = 2
        self.velocity[1] = -2
        self.air_time = 5
        self.jumps -= 1
      #Facing Right
      elif not self.flip and self.prev_movement[0] > 0:
        self.velocity[0] = -2
        self.velocity[1] = -2
        self.air_time = 5
        self.jumps -= 1
    elif self.jumps == 1:
      self.game.sfx['jump'][0].play(0)
      self.velocity[1] = -3
      self.jumps -= 1
      self.air_time = 5

  def dash(self):
    if not self.dashing:
      self.game.sfx['dash'][0].play(0)
      #facing left
      if self.flip:
        self.dashing = -60
      #facing right
      else:
        self.dashing = 60
