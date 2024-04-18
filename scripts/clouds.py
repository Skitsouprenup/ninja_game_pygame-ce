import random

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        #speed is a random number from 0.1 to 0.15(0.05 + 0.1) 
        self.speed = speed
        #depth is a random number from 0.2 to 0.8(0.6+0.2)
        #which make each cloud move at different rate
        #relative to the camera movement. This is called
        #the parallax effect.
        self.depth = depth
    
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, surf, offset):
        render_pos = (
          self.pos[0] - offset[0] * self.depth, 
          self.pos[1] - offset[1] * self.depth
        )
        surf.blit(
          self.img,
          #Create an effect where clouds reappear from 
          #left and top when they pass through to the right
          #and bottom. 
          #
          #First off, divide render_pos by surf.get_width() and
          #get the remainder but before that, add the image 
          #width to surf.get_width(). This ensures that clouds
          #will reappear to the left only if clouds width 
          #completely pass through the right side of screen. 
          #
          #Next, once we got the remainder, subtract it to the
          #cloud width again. This ensures if the cloud spawns to
          #the right, it will spawn at the blank side of the right side
          #instead of instantly appearing on right side of the screen.
          #If cloud is still moving on the screen, the subtracted image width
          #will offset clouds to the left which doesn't have an effect
          #on the movement of clouds.
          #
          #Example:
          #25 % (300 + 50) - 50 = 25 % 350 - 50 = 25 - 50 = -25
          #30 % (300 + 50) - 50 = 30 % 350 - 50 = 30 - 50 = -20
          #As you can see from the example above, clouds still moving to the right
          #Now, what if clouds pass through the right. Example:
          #355 % (300 + 50) - 50 = 355 % 350 - 50 = 5 - 50 = -45
          #As you can see from the example above, the cloud didn't spawn at 0
          #which is good because we don't want clouds to suddenly appear to the
          #left during the time the game is running. 
          ((render_pos[0] % (surf.get_width() + self.img.get_width())) - self.img.get_width(), 
           (render_pos[1] % (surf.get_height() + self.img.get_height())) - self.img.get_height())
        )
        
class Clouds:
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        
        for i in range(count):
            self.clouds.append(
              Cloud((random.random() * 99999, 
                     random.random() * 99999), 
              random.choice(cloud_images), 
              random.random() * 0.05 + 0.1, 
              random.random() * 0.6 + 0.2)
            )
        
        #sort clouds based on depth. Lowest depth
        #will be painted on the screen first and
        #highest depth will be painted last.
        self.clouds.sort(key=lambda x: x.depth)
    
    def update(self):
        for cloud in self.clouds:
            cloud.update()
    
    def render(self, surf, offset):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)