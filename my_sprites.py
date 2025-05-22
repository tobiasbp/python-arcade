import arcade


class Player(arcade.Sprite):
    """
    The player
    """

    def __init__(self, min_x_pos, max_x_pos, min_y_pos, max_y_pos, center_x=0, center_y=0, scale=1, angle=90):
        """
        Setup new Player object
        """

        # Limits on player's x position
        self.min_x_pos = min_x_pos
        self.max_x_pos = max_x_pos
        self.min_y_pos = min_y_pos
        self.max_y_pos = max_y_pos

        # Pass arguments to class arcade.Sprite
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            filename="images/playerShip1_red.png",
            scale=scale,
            flipped_diagonally=True,
            flipped_horizontally=True,
            angle=angle
        )

    def on_update(self, delta_time):
        """
        Move the sprite
        """

        # Update player's x position based on current speed in x dimension
        self.center_x += delta_time * self.change_x
        self.center_y += delta_time * self.change_y
        self.angle += delta_time * self.change_angle

        # Enforce limits on player's x position
        if self.left < self.min_x_pos:
            self.left = self.min_x_pos
        elif self.right > self.max_x_pos:
            self.right = self.max_x_pos

        if self.bottom < self.min_y_pos:
            self.bottom = self.min_y_pos
        elif self.top > self.max_y_pos:
            self.top = self.max_y_pos


class PlayerShot(arcade.Sprite):
    """
    A shot fired by the Player
    """

    def __init__(self, center_x, center_y, max_y_pos, speed=4, scale=1, angle=90):
        """
        Setup new PlayerShot object
        """

        # Set the graphics to use for the sprite
        # We need to flip it so it matches the mathematical angle/direction
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            scale=scale,
            filename="images/Lasers/laserBlue01.png",
            flipped_diagonally=True,
            flipped_horizontally=True,
            flipped_vertically=False,
        )

        # The shoot will be removed when it is above this y position
        self.max_y_pos = max_y_pos

        # Shoot points in this direction
        self.angle = angle

        # Shot moves forward. Sets self.change_x and self.change_y
        self.forward(speed)

    def on_update(self, delta_time):
        """
        Move the sprite
        """

        # Update the position of the sprite
        self.center_x += delta_time * self.change_x
        self.center_y += delta_time * self.change_y

        # Remove shot when over top of screen
        if self.bottom > self.max_y_pos:
            self.kill()
