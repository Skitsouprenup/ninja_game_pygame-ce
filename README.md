# ninja_game_pygame-ce
A simple 2D platformer game created using pygame-ce(Community Edition). This game is
not fully polished and only created for experimentation and learning purposes.

I have a demo video of this project in this [link](https://youtu.be/1-AQYvMeY20)

# Controls
These are the keys for the game.

## Game
Left Arrow: Left Movement  
Right Arrow: Right Movement  
Up Arrow: Up Movement  
Space: Dash(Attack Move)

## Editor
Left Click: Add Tile  
Right Click: Remove Tile  
Mouse Wheel Up or Down: Select Tile Set  
Shift + Mouse Wheel Up or Down: Select Tile Variant in Tile Set  
W: Move Up  
A: Move Left  
S: Move Down  
D: Move Right  
G: Switch between on-grid and off-grid tile mode
O: Save Level

# Running the game
To run the game, open a terminal in the game directory and type this command(python3):  
`python3 game.py`

To run the level editor of this game and create a new level, type this command(python3):  
`python3 editor.py`

If you want to edit a level, type this command(python3):  
`python3 editor.py edit <file-name>`  
Example: `python3 editor.py edit 0`  
No need to put a file extension.

# Notes about the level editor
Just like the game, the level editor is not fully polished. File names of levels must be a number from 0 above and they must be ordered and no number must be skipped. For example, your filenames are '0, 2, 4'. This will cause an error, your filenames must be: '0, 1, 2'.

On-grid tiles are tiles that are in grid space and can collide with other objects like
the player. Off-grid tiles are decoration tiles that don't collide with other objects.
