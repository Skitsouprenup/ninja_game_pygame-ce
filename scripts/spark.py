
import math

import pygame


class Spark:
  def __init__(self, pos, angle, speed):
    #pos may be a tuple. Convert it to list
    self.pos = list(pos)
    self.angle = angle #radians
    self.speed = speed

  def update(self):
    #Convert polar to cartesian. The hypotenuse or length
    #is the 'speed' variable.
    self.pos[0] += math.cos(self.angle) * self.speed
    self.pos[1] += math.sin(self.angle) * self.speed

    self.speed = max(0, self.speed - 0.1)
    return not self.speed
  
  def render(self, surf, offset):
    #Create a diamond shape polygon
    #In my assumption, 0 degree starts from the right due to inverted
    #cartesian.
    vertices = [
      #Arbitrary number '3' and '0.5' multiplied to speed 
      #is the length of vertex or how far the vertex is from the center of diamond
      #right vertex.
      (
        self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
        self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]
      ),
      #'math.pi * 0.5' is equal to 90 degrees
      #bottom vertex
      (
        self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0],
        self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]
      ),
      #'math.pi' is equal to 180 degrees
      #left vertex
      (
        self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0],
        self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]
      ),
      #top vertex
      (
        self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0],
        self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1]
      )
    ]

    pygame.draw.polygon(surf, (255, 255, 255), vertices)
