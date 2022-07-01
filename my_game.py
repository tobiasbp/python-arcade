"""
Simple program to show moving a sprite with the keyboard.

This program uses the Arcade library found at http://arcade.academy

Artwork from https://kenney.nl/assets/space-shooter-redux

"""
import random
from enum import Enum

import arcade


SPRITE_SCALING = 0.5
TILE_SCALING = 4
TILE_SIZE = TILE_SCALING * 16

# When Chuchu is closer to destination than this, it has arrived
IS_ON_TILE_DIFF = 2

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


class TileType(Enum):
    """
    Tiles with wall. Prefix T mean tile. next character is wall on x-axis, last character is wall on y-axis.
    """

    T__ = 0
    T_T = 1
    TR_ = 2
    T_B = 3
    TL_ = 4
    TLT = 5
    TRT = 6
    TRB = 7
    TLB = 8


class Tile(arcade.Sprite):
    """
    A tile :)
    """

    types = {
        0: {"out_dir": (0, 0), "image": "wall_none.png"},
        1: {"out_dir": (1, 0), "image": "wall_top.png"},
        2: {"out_dir": (0, -1), "image": "wall_right.png"},
        3: {"out_dir": (-1, 0), "image": "wall_bottom.png"},
        4: {"out_dir": (0, 1), "image": "wall_left.png"},
        5: {"out_dir": (1, 0), "image": "wall_top_left.png"},
        6: {"out_dir": (0, -1), "image": "wall_top_right.png"},
        7: {"out_dir": (-1, 0), "image": "wall_bottom_right.png"},
        8: {"out_dir": (0, 1), "image": "wall_bottom_left.png"},
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


class Chuchu(arcade.Sprite):
    """
    A Chuchu (AKA a mouse)
    """

    def __init__(self, my_emitter, my_speed=100, **kwargs):
        """
        Setup new Chuchu
        """
        # The direction I'm moving in
        self.my_direction = None

        # Steps per tile
        self.my_speed = my_speed

        # Graphics
        kwargs["filename"] = "images/Chuchu/Chuchu.png"

        # Scale the graphics
        kwargs["scale"] = TILE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        # All chuchus start at their emitter
        self.position = my_emitter.position

        # My first move is in emit direction
        self.move(my_emitter.emit_vector)

        self.waiting_for_orders = False

    def drained(self):
        """
        When a Chuchu reaches a drain and should no longer exist
        """

        print("I was drained. Yes!")
        self.kill()

    def move(self, new_direction):
        """
        Gets a direction and calculates destination screen coordinates
        """
        # If the tile doesn't require change in direction
        # I will continue in current direction
        if not new_direction is (0, 0):
            # Current direction is updated
            self.my_direction = new_direction

        # x and y position of destination tile
        self.my_destination_screen_coordinates = [
            n * TILE_SIZE for n in self.my_direction
        ]

        self.my_destination_screen_coordinates[0] += self.center_x
        self.my_destination_screen_coordinates[1] += self.center_y

        # Calculating speed by (new destination - current destination) / number of steps
        self.change_x = (
            self.my_destination_screen_coordinates[0] - self.center_x
        ) / self.my_speed
        self.change_y = (
            self.my_destination_screen_coordinates[1] - self.center_y
        ) / self.my_speed

        self.waiting_for_orders = False

    def update(self, delta_time):
        """
        Move sprite
        """
        # FIXME: use delta_time
        if (
            arcade.get_distance(
                self.my_destination_screen_coordinates[0],
                self.my_destination_screen_coordinates[1],
                self.position[0],
                self.position[1],
            )
            > IS_ON_TILE_DIFF
        ):
            self.center_x += self.change_x
            self.center_y += self.change_y
        else:
            self.position = self.my_destination_screen_coordinates
            self.waiting_for_orders = True


class Emitter(arcade.Sprite):
    """
    An emitter spawning chuchus
    """

    emitter_types = {0: "images/Emitter/Emitter_jar.png"}

    def __init__(
        self, on_tile, type=0, capacity=5, emit_vector=(-1, 0), emit_rate=2.0, **kwargs
    ):
        """
        Setup new Emitter
        """

        # How fast will Chuchus spawn
        self.emit_rate = emit_rate

        # Ready to emit a chuchu
        self.emit_timer = 0

        self.capacity = capacity

        kwargs["filename"] = Emitter.emitter_types[type]
        kwargs["scale"] = TILE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        self.go_to_tile(on_tile)

        # Direction for the outspitted Chuchus
        self.emit_vector = emit_vector

        # Create queue for waiting Chuchus
        self.chuchus_queue = arcade.SpriteList()
        for n in range(capacity):
            self.chuchus_queue.append(Chuchu(self))

    @property
    def no_emitted(self):
        return self.capacity - len(self.chuchus_queue)

    def go_to_tile(self, tile):
        self.on_tile = tile
        self.position = self.on_tile.position

    def get_chuchu(self):

        if any(self.chuchus_queue) and self.emit_timer <= 0:
            self.emit_timer = self.emit_rate
            c = self.chuchus_queue.pop()
            print(f"Nunber of Chuchus emitted: {self.no_emitted}")
            return c

    def update(self, delta_time):
        if self.emit_timer > 0:
            self.emit_timer -= delta_time


class Drain(arcade.Sprite):
    """
    A Drain for draining Chuchus
    """

    def __init__(self, on_tile, **kwargs):
        kwargs["filename"] = "images/Drain/Drain_cream.png"
        kwargs["scale"] = TILE_SCALING

        # Pass arguments to class arcade.Sprite
        super().__init__(**kwargs)

        self.position = on_tile.position

        # Number of Chuchus drained
        self.no_drained = 0

    def drained(self, chuchu):
        """
        <chuchu> has been drained by me
        """
        self.no_drained += 1
        print(f"I have drained a total number of {self.no_drained} chuchus :D")


class TileMatrix:
    """
    Matrix of Tile(s) >:)
    Consists of chuchus
    """

    def __init__(
        self,
        level_data,
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
            t = Tile(type=level_data["tiles"][i])
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
        # Find tile to stand on
        emitter_dest_tile = self.matrix[level_data["emitter"]["pos"]]
        # Create emitter and tell it where to stand
        emitter = Emitter(emitter_dest_tile, type=level_data["emitter"]["image"])
        self.add_emitter(emitter)

        # Create list for drains
        self.drains = arcade.SpriteList()
        self.add_drain(Drain(self.matrix[level_data["drain"]["pos"]]))

    @property
    def level_clear(self):
        # If all Chuchus are drained, level ends :P
        if sum([d.no_drained for d in self.drains]) is sum(
            [e.capacity for e in self.emitters]
        ):
            return True
        else:
            return False

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

    def add_emitter(self, emitter: arcade.Sprite):
        """
        Append emitter to list of emitters
        """
        self.emitters.append(emitter)

    def add_drain(self, drain: arcade.Sprite):
        """
        Append drain to list of drains
        """
        self.drains.append(drain)

    def get_sprite_from_screen_coordinates(self, coordinates, sprite_list):
        """
        Returns a sprite from <sprite_list> matching screen <coordinates>
        """
        for t in sprite_list:
            if (
                arcade.get_distance(
                    t.position[0], t.position[1], coordinates[0], coordinates[1]
                )
                < IS_ON_TILE_DIFF
            ):
                return t
        return None

    def draw(self):
        self.matrix.draw()
        self.emitters.draw()
        self.drains.draw()
        self.chuchus.draw()
        self.players.draw()

    def update(self, delta_time):

        # Pull chuchus from emitters
        for e in self.emitters:
            c = e.get_chuchu()

            if c is not None:
                self.chuchus.append(c)

            # Update emitter
            e.update(delta_time)

        # Handle waiting Chuchus
        for c in self.chuchus:
            if c.waiting_for_orders is True:

                # Is Chuchu on a drain
                current_drain = self.get_sprite_from_screen_coordinates(
                    c.position, self.drains
                )
                if not current_drain is None:
                    c.drained()
                    current_drain.drained(c)

                    # Nothing more to do for this Chuchu
                    break

                # FIXME
                # Out_dir dur jo ikke hvis man kommer fra den forkerte side.
                # Eks:
                # Vi har en tile i toppen med en væg kun på toppen.
                # Der kommer en Chuchu fra højre.
                # Tilens out_dir er til højre, så Chuchu drejer til højre selvom den kommer fra højre, uden at støde ind i væg (den går baglæns)

                # Look at tiles
                current_tile = self.get_sprite_from_screen_coordinates(
                    c.position, self.matrix
                )
                assert current_tile is not None, "Chuchu was not on any tile"
                c.move(current_tile.my_type["out_dir"])

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

    def update(self, delta_time):
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
            "emitter": {"pos": (4), "image": 0},
            "drain": {"pos": (5)},
        },
        2: {
            "tiles": [8, 3, 3, 3, 7]
            + [4, 0, 0, 0, 2]
            + [4, 0, 2, 4, 2]
            + [4, 0, 2, 4, 2]
            + [5, 1, 6, 5, 6],
            "emitter": {"pos": (1), "image": 0},
            "drain": {"pos": (2)},
        },
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

        # What level is it
        self.level = None

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

        # Start at level 1
        self.level = 1

        self.start_level()

    def start_level(self):
        # Create tile matrix
        assert (
            self.level in MyGame.levels.keys()
        ), f"Error: no data for level {self.level}"
        self.tile_matrix = TileMatrix(level_data=MyGame.levels[self.level])

    def end_level(self):
        self.level += 1
        self.start_level()

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
        # self.player_shot_list.update()

        self.tile_matrix.update(delta_time)

        if self.tile_matrix.level_clear:
            self.end_level()

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
