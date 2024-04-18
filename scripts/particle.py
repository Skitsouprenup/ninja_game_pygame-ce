class Particle:
    def __init__(self, game, type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.animations['particle/' + type].shallow_copy()
        self.animation.frame = frame
    
    def update(self):
        kill = False
        if self.animation.complete:
            kill = True
        
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        self.animation.update()
        
        return kill
    
    def render(self, surf, offset=(0, 0)):
        img = self.animation.image()
        #Position
        surf.blit(img, (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1])))
    