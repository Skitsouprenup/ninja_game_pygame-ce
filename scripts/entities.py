import pygame

class PhysicsEntity:
    def __init__(self, game, type, pos, size):
        self.game = game
        self.type = type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        #this offset is a spacing around the object.
        #Some animation images may unintentionally overlap
        #with another image ley's say a wall image. 
        #One of the reason for this is that the image 
        #is larger than its collision box.
        #Remove this if your image is not unintentionally
        #overlapping with another image.
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

    def rect(self):
      return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
    def set_action(self, action):
        #If there's a new action, replace
        #the current action which also
        #replace the current animation
        if(action != self.action):
            self.action = action
            self.animation = self.game.animations[self.type + '/' + self.action].shallow_copy()

    def update(self, tilemap, movement=(0, 0)):
        #init collisions
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        tilemaps = tilemap.closest_collision_tiles(self.pos)

        #apply change in y of an object.
        self.pos[1] += frame_movement[1]
        #update object collision box position
        entity_rect = self.rect()
        for rect in tilemaps:
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        #apply change in x of an object first. This is important because
        #we want to handle collision per axis. This collision algorithm
        #won't work if we apply change in x and y at the same time.
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemaps:
            #pygame.draw.rect(self.game.display, 'RED', rect)

            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        #Check if entity is moving left or right.
        #If entity move left, flip the image to the
        #left. Otherwise, image should remain in its
        #original direction which is right
        if frame_movement[0] > 0:
            self.flip = False
        elif frame_movement[0] < 0: 
            self.flip = True
        
        #Simulate gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        #When object is on the ground
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()
        
    def render(self, surf, offset, non_silhouette=None):
        surface = surf

        if non_silhouette is not None:
          surface = non_silhouette

        #flip image from left to right and vice versa. The third parameter of
        #flip is set to false because we don't want to flip the image from top
        #to bottom and vice versa.
        surface.blit(
          pygame.transform.flip(
            self.animation.image(), 
            self.flip, 
            False
          ),
          #Convert self.pos[1] to int or else you will have a jitter
          #problem when camera 'y' offset is very close to
          #self.pos[1].
          (
            int(self.pos[0]) - offset[0] + self.anim_offset[0], 
            int(self.pos[1]) - offset[1] + self.anim_offset[1]
          )
        )
        