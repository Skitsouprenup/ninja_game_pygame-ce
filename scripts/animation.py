class Animation:
  def __init__(self, images, loop=True, frame_duration=5):
    self.images = images
    #frame_duration is a padding in between images
    #that is used to control animation speed.
    #For example, you want to animate a slash
    #animation at 30 frames and the animation has
    #5 frames. To achieve this, set the frame_duration
    #to 6 and then multiply it by the number of images:
    #5 * 6 = 30
    #Now, the animation will run at 30 fps
    self.frame_duration = frame_duration
    self.loop = loop
    self.complete = False
    self.frame = 0

  def shallow_copy(self):
    return Animation(self.images, self.loop, self.frame_duration)
  
  def update(self):
    if self.loop:
      #If animation is looping, we use modulo to loop through frames.
      #For example, initial value of self.frame is 0, frame_duration is 6
      #and number of images is 5
      #(0 + 1) % (6 * 5) = 1 % 30 = 1
      #(1 + 1) % (6 * 5) = 2 % 30 = 2
      #....
      #(29 + 1) % (6 * 5) = 30 % 30 = 0
      self.frame = (self.frame + 1) % (self.frame_duration * len(self.images))
    else: 
      #If animation is not looping, we don't need to use module here and instead
      #use min() to iterate through frames. Make sure to subtract the second
      #parameter by 1 because animation images are stored in list which is a
      #zero-based index.
      self.frame = min(self.frame + 1, (self.frame_duration * len(self.images)) - 1)
      #If last frame is reached set self.complete value to True
      if self.frame >= (self.frame_duration * len(self.images)) - 1:
        self.complete = True

  def image(self):
    #Get the current animation frame. This is how
    #the computation here works:
    #Let's say, frame_duration is 3
    #0 / 3 = 0
    #1 / 3 = 0
    #2 / 3 = 0
    #3 / 3 = 1
    #4 / 3 = 1
    #5 / 3 = 1
    #6 / 3 = 2
    #and so on...
    return self.images[int(self.frame / self.frame_duration)]