import math
import random
import sys

import pygame

from scripts.clouds import Clouds
from scripts.factory import Factory
from scripts.particle import Particle
from scripts.player import Player
from scripts.spark import Spark
from scripts.tilemap import Tilemap
from scripts.constants import \
  init_assets, init_anims, init_sfx, \
  SCREEN_TRANSITION_DURATION, \
  MAX_LEVEL
from scripts.utils import create_outline

class Game:
    def __init__(self):
        pygame.init()

        self.sfx = init_sfx()

        pygame.mixer.music.load('data/music.wav')
        #music volume
        pygame.mixer.music.set_volume(0.5)
        #-1 means infinite looping
        pygame.mixer.music.play(-1)

        self.sfx['ambience'][0].play(-1)

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        #pygame.SRCALPHA adds a tranparency channel to our
        #surface
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.non_silhouette = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.factory = Factory()

        self.assets = init_assets()

        self.animations = init_anims()

        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.screenshake = 0

        self.player = Player(self, (0, 0), (10, 13))
        self.dead = 0

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.load_level('data/maps/'+str(self.level)+'.json')
        self.transition = -(SCREEN_TRANSITION_DURATION)

    def load_level(self, path):
      self.tilemap.load_map(path)
      #This should be subtracted to every objects to achieve
      #the camera effect. Objects should move opposite to camera
      #movement.
      self.scroll = [0, 0]

      self.projectiles = []
      self.particles = []
      self.sparks = []

      self.leaf_spawners = []
      self.enemy_spawner = []
      
      #Extract tree tile in 'large_decor' tile set on the screen
      self.leaf_spawners = \
        self.factory.create_leaf_spawner(self.tilemap.extract([('large_decor', 2)], True))
      
      self.enemy_spawner = self.factory.create_character_spawner(
        self,
        self.player,
        #We just want to get the spawner here. Thus, keep should be false
        #so that it won't be added in the tile list.
        self.tilemap.extract([('spawner', 0), ('spawner', 1)])
      )

    def create_sparks(self, n_sparks, p_pos, r_angle, r_speed):
      for i in range(n_sparks):
        self.sparks.append(Spark(p_pos,r_angle,r_speed))

    def explode_entity(self, n_objects, spark_spawn, particle_spawn):
      for i in range(n_objects):
        #get one random angle from a full circle
        r_angle = random.random() * math.pi * 2
        r_speed = random.random() * 2
        self.sparks.append(
        Spark(
          spark_spawn,
          r_angle,
          r_speed
        )
        )
        self.particles.append(
          Particle(
            self, 
            'dash',
            particle_spawn,
            [
              math.cos(r_angle + math.pi) * r_speed,
              math.sin(r_angle + math.pi) * r_speed
            ],
            random.randint(0, 7)
          )
        )

    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            #background
            self.non_silhouette.blit(
              pygame.transform.scale(self.assets['background'], self.screen.get_size()), 
              (0, 0))

            #if screenshake is greater than 0, reduce it
            #until it reaches 0.
            self.screenshake = max(0, self.screenshake - 1)

            #If all enemies are dead
            if not len(self.enemy_spawner):
              #Gradually hide the level.
              self.transition += 1
              #If transition reaches 30 frames or half a second,
              #load new level.
              if self.transition > SCREEN_TRANSITION_DURATION:
                 self.level = (self.level + 1) % MAX_LEVEL
                 self.transition = -(SCREEN_TRANSITION_DURATION)
                 self.load_level('data/maps/'+str(self.level)+'.json')
            #When starting a new level, the screen is full black
            #and transition is negative. As self.transition moves back
            #to 0 from a negative number, the level becomes visible.
            if self.transition < 0:
              self.transition += 1

            #If player dies
            if self.dead:
              self.dead += 1
              #30 = 0.5secs
              if self.dead > 30:
                 self.load_level('data/maps/'+str(self.level)+'.json')
                 self.dead = 0
                 self.transition = -(SCREEN_TRANSITION_DURATION)
              else:
                self.transition += 1
                 
            #First get the distance between the center of the display(game screen)
            #and the player's centerx and then move the camera by the distance that we computed
            #For example, the camera's 'x' is 0; player's centerx = 50; display centerx = 150
            #50 - 150 - 0 = -100
            #the result is negative and thus the camera will move to the left.
            
            #Next, move the player based on the result above.
            #player's 'centerx' is 50 and thus its 'x' is 25, subtract that to
            #-100 and we got -75

            #Now, if we calculate the distance between the camera's 'x' to player's centerx
            #the result is 150(|-100 + -50|) which is the center of the screen and now the
            #player is on the center of the screen and camera.

            #Now, let's update the player's centerx to 60.
            #60 - 150 - 100 = -90 - 100 = 10
            #The result is positive and thus the camera will move to the right.
            #Now, if we calculate the distance between the camera's 'x' to player's centerx
            #(100 - 10) + 60 = 90 + 60 = 150
            #The player is still in the middle of the display and camera.

            #What if the player didn't move? The result will be zero and thus no addition
            #to scroll[0]. Take a look at this example:
            #60 - 150 - 90 = 90 - 90 = 0

            #Now, to add a 'delay-follow' effect where the camera follows the player
            #with delay instead of instant, we need to divide the result by some amount.
            #In this case, I choose 30 because its half of the current FPS of this game.
            #This makes the camera follow the player with the delay of 1/30
            #This makes the camera possibly catch up to player by 30 frames.
            #Example:
            #40 - 150 - 0 = -90 / 30 = -3
            #Now, the camera will move -3 pixels in x-coordinate per frame which is
            #equivalent to -90 at 30 frames.
            self.scroll[0] += (self.player.rect().centerx - (self.display.get_width() * 0.5) - self.scroll[0]) #/ 30
            self.scroll[1] += (self.player.rect().centery - (self.display.get_height() * 0.5) - self.scroll[1]) #/ 30
            #
            int_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #clouds
            self.clouds.update()
            self.clouds.render(self.non_silhouette, offset=int_scroll)

            for rect in self.leaf_spawners:
              if random.randint(0, 100) < 3:
                #Get random x and y coordinates within the width and height of spawner objects
                #For example, tree object.
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                #Create 'leaf' particle with random pos, velocity and initial frame image
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.15, 0.5], frame=random.randint(5, 15)))

            #[[x, y], direction, timer]
            for projectile in self.projectiles.copy():
              projectile[0][0] += projectile[1]
              projectile[2] += 1
              bullet = self.assets['projectile']
              self.display.blit(
                bullet, 
                [
                  int(projectile[0][0] - bullet.get_width() * 0.5) - int_scroll[0],
                  int(projectile[0][1] - bullet.get_height() * 0.5) - int_scroll[1]
                ]
              )
              if self.tilemap.solid_tile(projectile[0]):
                self.projectiles.remove(projectile)
                self.create_sparks(
                  6,
                  projectile[0],
                  #Create a spark opposite to the wall. If
                  #projectile comes from right and wall is on the left,
                  #add math.pi in order for the sparks to come out from
                  #the right side of the wall.
                  random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                  1 + random.random()
                )
              #300 = 60 * 5 = 5secs
              #60 = 1sec which is based on our FPS(60)
              elif projectile[2] > 300:
                self.projectiles.remove(projectile)
              #If player is not dashing
              elif abs(self.player.dashing) < 50:
                #If projectile hits the player
                if self.player.rect().collidepoint(projectile[0]):
                  self.sfx['hit'][0].play(0)
                  self.projectiles.remove(projectile)
                  self.dead = 1
                  self.screenshake = max(12, self.screenshake)

                  self.explode_entity(
                    15, 
                    self.player.rect().center,
                    #Assigning the center here doesn't make the
                    #particles spawn at center. This works for
                    #some reason.
                    (self.player.rect().x, self.player.rect().y)
                  )

            for spark in self.sparks:
               kill = spark.update()
               spark.render(self.display, offset=int_scroll)
               if kill:
                  self.sparks.remove(spark)

            for particle in self.particles:
                kill = particle.update()
                particle.render(self.display, offset=int_scroll)
                if particle.type == 'leaf':
                    #We use math.sin() to control the swinging effect of leaves.
                    #We use the frame * 0.15 as radian(angle)
                    #For example, the product is 0.785 radians which is 45 degrees.
                    #If we compute the sin with the product, the result is ~0.7
                    #If the degree is like 200, the result is going to be ~(-0.34)
                    #As you can see, the result can be positive or negative depends
                    #on the input angle.
                    particle.pos[0] += math.sin(particle.animation.frame * 0.15)
                if kill:
                    self.particles.remove(particle)

            #tilemaps
            self.tilemap.render(self.display, offset=self.scroll)

            #enemy
            for enemy in self.enemy_spawner:
              kill = enemy.update(self.tilemap, (0, 0))
              enemy.render(self.display, int_scroll)
              if kill:
                 self.enemy_spawner.remove(enemy)

            #player
            if not self.dead:
              self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
              self.player.render(self.display, self.non_silhouette, offset=int_scroll)
            #events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_SPACE:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            if self.transition:
              transition_surf = pygame.Surface(self.display.get_size())
              #radius per frame
              #divide screen width to 30 frames which is half a second
              rad_per_frame = int(self.display.get_width() / SCREEN_TRANSITION_DURATION)
              radius = 0

              if self.transition > 0:
                #Reduce radius to 0 or near 0
                radius = (self.display.get_width() - (rad_per_frame * self.transition))
              else:
                #Increase radius from near 0 or 0 to screen width
                radius = rad_per_frame * (SCREEN_TRANSITION_DURATION - abs(self.transition))

              pygame.draw.circle(
                transition_surf, 
                (255, 255, 255),
                #Circle's center
                (
                  int(self.display.get_width() * 0.5),
                  int(self.display.get_height() * 0.5)
                ),
                radius
              )
              transition_surf.set_colorkey((255, 255, 255))
              self.display.blit(transition_surf, (0, 0))

            #First off we get a random number from 0 to self.screenshake.
            #then we multiply it by (self.screenshake * 0.5). We use the
            #half value of screenshake to decide if x or y coordinate is
            #a positive or negative. If half of screenshake is greater than
            #the random number, the result is negative.
            screenshake_offset = (
              random.random() * self.screenshake - self.screenshake * 0.5,
              random.random() * self.screenshake - self.screenshake * 0.5
            )
            
            create_outline(self.non_silhouette, self.display)
            self.screen.blit(
              pygame.transform.scale(self.non_silhouette, self.screen.get_size()), 
              screenshake_offset
            )
            pygame.display.update()
            self.clock.tick(60)

Game().run()