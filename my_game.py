"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""
import random
import arcade


SPRITE_SCALING = 0.5
TILE_SCALING = 4
TILE_SIZE = TILE_SCALING * 16

# Set the size of the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Variables controlling the player
PLAYER_LIVES = 3
PLAYER_SPEED_X = 5
PLAYER_START_X = SCREEN_WIDTH / 2
PLAYER_START_Y = 50
PLAYER_SHOT_SPEED = 4

FIRE_KEY = arcade.key.SPACE


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, tile_pos, **kwargs):
        """
        Setup new Player object
        """
        self.tile_pos = tile_pos

        # Graphics to use for Player
        kwargs["filename"] = "images/playerShip1_red.png"

        # How much to scale the graphics
        kwargs["scale"] = SPRITE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

    def update(self, delta_time):
        """
        Move the sprite
        """
        pass


class Tile(arcade.Sprite):
    """
    A tile :)
    """

    types = {
        0: {"out_dir": 0, "image": "wall_none.png"},
        1: {"out_dir": 2, "image": "wall_top.png"},
        2: {"out_dir": 3, "image": "wall_right.png"},
        3: {"out_dir": 4, "image": "wall_bottom.png"},
        4: {"out_dir": 1, "image": "wall_left.png"},
        5: {"out_dir": 2, "image": "wall_top_left.png"},
        6: {"out_dir": 3, "image": "wall_top_right.png"},
        7: {"out_dir": 4, "image": "wall_bottom_right.png"},
        8: {"out_dir": 1, "image": "wall_bottom_left.png"},
    }

    def __init__(self, type=0, **kwargs):
        """
        Setup new Tile object
        """
        self.my_type = Tile.types[type]

        # Graphics to use for Tile
        kwargs["filename"] = f'images/Tiles/{self.my_type["image"]}'

        # How much to scale the graphics
        kwargs["scale"] = TILE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)


class Emitter(arcade.Sprite):
    """
    An emitter spawning chuchus
    """

    emitter_types = {0: {"image": "images/Emitter/Emitter_jar.png"}}

    def __init__(self, on_tile, type=0, **kwargs):
        """
        Setup new Emitter
        """
        kwargs["filename"] = Emitter.emitter_types[type]["image"]
        kwargs["scale"] = TILE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)
        self.go_to_tile(on_tile)

    def go_to_tile(self, tile):
        self.on_tile = tile
        self.position = self.on_tile.position


class TileMatrix:
    """
    Matrix of Tile(s) >:)
    Consists of chuchus
    """

    def __init__(
        self,
        tile_types,
        matrix_width=5,
        matrix_height=5,
        tile_size=TILE_SIZE,
        matrix_offset_x=200,
        matrix_offset_y=200,
    ):
        # Create matrix
        self.matrix = arcade.SpriteList()

        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.matrix_offset_x = matrix_offset_x
        self.matrix_offset_y = matrix_offset_y

        # Append tiles to matrix
        for i in range(matrix_width * matrix_height):
            t = Tile(type=tile_types[i])
            t.center_x = ((i % matrix_width) * tile_size) + matrix_offset_x
            t.center_y = ((i // matrix_height) * tile_size) + matrix_offset_y
            self.matrix.append(t)

        # Create list for chuchus
        self.chuchus = arcade.SpriteList()

        # Create list for Players
        self.players = arcade.SpriteList()
        # Append player to playerlist with start position
        self.players.append(Player(tile_pos=(1, 1)))

        # Create list for Emitters
        self.emitters = arcade.SpriteList()
        on_tile = random.choice(self.matrix)
        emitter = Emitter(on_tile)
        self.add_emitter(emitter)

    def move_player(self, player_no, dir):
        """
        The player is moved
        """
        current_pos = self.players[player_no].tile_pos
        new_pos = (current_pos[0] + dir[0], current_pos[1] + dir[1])

        # Check if new position is legal
        if not -1 < new_pos[0] < self.matrix_width:
            return
        if not -1 < new_pos[1] < self.matrix_height:
            return

        # Update player position
        self.players[player_no].tile_pos = new_pos

    def add_emitter(self, emitter):
        """
        An emitter is added and placed
        """
        self.emitters.append(emitter)

    def draw(self):
        self.matrix.draw()
        self.emitters.draw()
        self.chuchus.draw()
        self.players.draw()

    def update(self, delta_time):
        for c in self.chuchus:
            c.update(delta_time)

        for p in self.players:
            p.update(delta_time)
            p.center_x = p.tile_pos[0] * TILE_SIZE + self.matrix_offset_x
            p.center_y = p.tile_pos[1] * TILE_SIZE + self.matrix_offset_y


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    def __init__(self, center_x=0, center_y=0):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the sprite
        super().__init__("images/Lasers/laserBlue01.png", SPRITE_SCALING)

        self.center_x = center_x
        self.center_y = center_y
        self.change_y = PLAYER_SHOT_SPEED

    def update(self):
        """
        Move the sprite
        """

        # Update y position
        self.center_y += self.change_y

        # Remove shot when over top of screen
        if self.bottom > SCREEN_HEIGHT:
            self.kill()


class MyGame(arcade.Window):
    """
    Main application class.
    """

    # Drawn upside down
    levels = {
        1: {
            "tiles": [8, 3, 3, 3, 7]
            + [4, 0, 0, 0, 2]
            + [4, 0, 0, 0, 2]
            + [4, 0, 0, 0, 2]
            + [5, 1, 1, 1, 6],
            "emitter": {"pos": (0, 0), "image": 0},
        }
    }

    def __init__(self, width, height):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height)

        # Variable that will hold a list of shots fired by the player
        self.player_shot_list = None

        # Set up the player info
        self.player_sprite = None
        self.player_score = None
        self.player_lives = None

        # Set up matrix
        self.tile_matrix = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Get list of joysticks
        joysticks = arcade.get_joysticks()

        if joysticks:
            print("Found {} joystick(s)".format(len(joysticks)))

            # Use 1st joystick found
            self.joystick = joysticks[0]

            # Communicate with joystick
            self.joystick.open()

            # Map joysticks functions to local functions
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyaxis_motion = self.on_joyaxis_motion
            self.joystick.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("No joysticks found")
            self.joystick = None

            # self.joystick.
        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """Set up the game and initialize the variables."""

        # No points when the game starts
        self.player_score = 0

        # No of lives
        self.player_lives = PLAYER_LIVES

        # Sprite lists
        self.player_shot_list = arcade.SpriteList()

        # Create tile matrix
        self.tile_matrix = TileMatrix(tile_types=MyGame.levels[1]["tiles"])

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the player shot
        self.player_shot_list.draw()

        # Draw players score on screen
        arcade.draw_text(
            "SCORE: {}".format(self.player_score),  # Text to show
            10,  # X position
            SCREEN_HEIGHT - 20,  # Y positon
            arcade.color.WHITE,  # Color of text
        )

        # Draw matrix on screen
        self.tile_matrix.draw()

    def on_update(self, delta_time):
        """
        Movement and game logic
        """

        # Update the player shots
        self.player_shot_list.update()

        self.tile_matrix.update(delta_time)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """

        # Track state of arrow keys
        if key == arcade.key.UP:
            self.up_pressed = True
            self.tile_matrix.move_player(0, (0, 1))
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            self.tile_matrix.move_player(0, (0, -1))
        elif key == arcade.key.LEFT:
            self.left_pressed = True
            self.tile_matrix.move_player(0, (-1, 0))
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.tile_matrix.move_player(0, (1, 0))

        if key == FIRE_KEY:
            new_shot = PlayerShot(
                self.player_sprite.center_x, self.player_sprite.center_y
            )

            self.player_shot_list.append(new_shot)

    def on_key_release(self, key, modifiers):
        """
        Called whenever a key is released.
        """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_joybutton_press(self, joystick, button_no):
        print("Button pressed:", button_no)
        # Press the fire key
        self.on_key_press(FIRE_KEY, [])

    def on_joybutton_release(self, joystick, button_no):
        print("Button released:", button_no)

    def on_joyaxis_motion(self, joystick, axis, value):
        print("Joystick axis {}, value {}".format(axis, value))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Joystick hat ({}, {})".format(hat_x, hat_y))


def main():
    """
    Main method
    """

    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
