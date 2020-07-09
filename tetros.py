#! python3

import random
import pygame
from pygame.locals import *


pygame.init()
pygame.font.init()

# GLOBAL CONSTANTS

WINDOW_WIDTH = 850
PLAY_AREA_WIDTH = 480
PLAY_AREA_HEIGHT = 880
WINDOW_HEIGHT = 1000
SCORE_HEIGHT = 100
SCORE_WIDTH = 250
NEXT_PIECE_SIZE = 180
GRID_SIZE = 40
STAT_FONT = pygame.font.SysFont("comicsans", 40)
TEXT_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (50, 60, 180)
PAUSE_COLOR = (20, 20, 20, 100)
BANNER_COLOR = (110, 110, 110)
GRID_COLOR = (200, 200, 200)

SHAPES = ("I", "O", "T", "S", "Z", "J", "L")
COLORS = [
    (0, 255, 255),
    (255, 255, 0),
    (128, 0, 128),
    (0, 128, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 165, 0)
]


class Tetromino:
    """Class used to create Tetromino objects

    Returns:
        [Tetromino object]:
        [has a shape, a bounding box,
        and functions associated with
        drawing and moving the object.]
    """

    DROP_RATE = 5

    def __init__(self, shape):
        self.shape = shape
        self.set_blocks()
        self.falling = True
        self.tick_count = 0
        if self.shape == "I" or self.shape == "O":
            self.bounding_box = pygame.Rect(
                int(PLAY_AREA_WIDTH / 2) - GRID_SIZE * 2,
                -120,
                (GRID_SIZE * len(self.blocks)),
                (GRID_SIZE * len(self.blocks))
            )
        else:
            self.bounding_box = pygame.Rect(
                int(PLAY_AREA_WIDTH / 2) - GRID_SIZE,
                -200,
                (GRID_SIZE * len(self.blocks)),
                (GRID_SIZE * len(self.blocks))
            )
        self.squares = []
        for x in range(len(self.blocks)):
            for y in range(len(self.blocks)):
                if self.blocks[y][x]:
                    self.squares.append(pygame.Rect(
                        (self.bounding_box.left + GRID_SIZE * x),
                        (self.bounding_box.top + GRID_SIZE * y),
                        GRID_SIZE,
                        GRID_SIZE
                    ))
        for i, SHAPE in enumerate(SHAPES):
            if self.shape == SHAPE:
                self.color = COLORS[i]

    def deepcopy(self):
        """Creates a deepcopy of the object it is called on.

        Returns:
            Tetromino object: Used to display the next piece in the window to
            the side of the play area. A deepcopy is needed to ensure that the
            position of the next piece isn't changed while drawing it in the
            next piece window.
        """
        return Tetromino(self.shape)

    def set_blocks(self):
        """Uses the string version of the Tetromino's shape to generate an
        array that can be used to draw and rotate the Tetromino.
        """
        if self.shape == "I":
            self.blocks = [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        elif self.shape == "O":
            self.blocks = [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0]
            ]
        elif self.shape == "T":
            self.blocks = [
                [0, 1, 0],
                [1, 1, 1],
                [0, 0, 0]
            ]
        elif self.shape == "S":
            self.blocks = [
                [0, 1, 1],
                [1, 1, 0],
                [0, 0, 0]
            ]
        elif self.shape == "Z":
            self.blocks = [
                [1, 1, 0],
                [0, 1, 1],
                [0, 0, 0]
            ]
        elif self.shape == "J":
            self.blocks = [
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 0]
            ]
        elif self.shape == "L":
            self.blocks = [
                [0, 0, 0],
                [1, 1, 1],
                [1, 0, 0]
            ]

    def rotate(self):
        """Rotates the Tetromino clockwise
        """
        rotated = [[] for _ in range(len(self.blocks))]
        for x in range(len(self.blocks)):
            for y in range(len(self.blocks)):
                rotated[x].append(self.blocks[abs(y-(len(self.blocks)-1))][x])
        self.blocks = rotated

    def rotate_cc(self):
        """Rotates the Tetromino counterclockwise
        """
        rotated = [[] for _ in range(len(self.blocks))]
        for x in range(len(self.blocks)):
            for y in range(len(self.blocks)):
                rotated[x].append(self.blocks[y][abs(x-(len(self.blocks)-1))])
        self.blocks = rotated

    def draw(self, surface):
        """Draws the Tetromino onto the surface given.

        Args:
            surface (pygame surface): designates which pygame surface to draw
            the Tetromino onto.
        """
        self.squares = []
        for x in range(len(self.blocks)):
            for y in range(len(self.blocks)):
                if self.blocks[y][x]:
                    self.squares.append(pygame.Rect(
                        (self.bounding_box.left + GRID_SIZE * x),
                        (self.bounding_box.top + GRID_SIZE * y),
                        GRID_SIZE,
                        GRID_SIZE
                    ))
        for square in self.squares:
            pygame.draw.rect(surface, self.color, square)

    def fall(self, level):
        """Makes the Tetromino fall over time.

        Args:
            level (int): The current level that the player is on,
            based on the number of rows they have cleared. At higher levels,
            the Tetrominos will fall faster.
        """
        if self.falling == True:
            self.tick_count += (level / 2)
            if self.tick_count > self.DROP_RATE:
                self.bounding_box.top += GRID_SIZE
                self.tick_count = 0

    def drop(self, placed_blocks):
        """Drops the Tetromino much more quickly than normal.

        Args:
            placed_blocks (list): A list containing the pygame rectangles
            for every block already placed on the level from pieces that
            have already fallen and become fixed in place, but haven't been
            cleared by completing a row.
        """
        self.DROP_RATE = 0.5

    def shift(self, direction, placed_blocks):
        """Shifts the Tetromino one column to the left or right.

        Args:
            direction (string): A string telling the function which direction
            the user input specifies the Tetromino should move.
            placed_blocks (list): A list containing the pygame rectangles
            for every block already placed on the level from pieces that
            have already fallen and become fixed in place, but haven't been
            cleared by completing a row.
        """
        left_edge = PLAY_AREA_WIDTH
        right_edge = 0
        top = []
        can_move = False
        if not placed_blocks:
            can_move = True
        if direction == "left":
            for square in self.squares:
                if square.left < left_edge:
                    left_edge = square.left
                top.append(square.top)
            try:
                for block in placed_blocks:
                    if block[0].right == left_edge and block[0].top in top:
                        can_move = False
                    elif left_edge < GRID_SIZE:
                        can_move = False
                    else:
                        can_move = True
            except:
                pass
            if can_move == True:
                self.bounding_box.left -= GRID_SIZE

        elif direction == "right":
            for square in self.squares:
                if square.right > right_edge:
                    right_edge = square.right
                top.append(square.top)
            try:
                for block in placed_blocks:
                    if block[0].left == right_edge and block[0].top in top:
                        can_move = False
                    elif right_edge == PLAY_AREA_WIDTH:
                        can_move = False
                    else:
                        can_move = True
            except:
                pass
            if can_move == True:
                self.bounding_box.left += GRID_SIZE


def draw_window(window, play_area, score_area, next_piece, tetrominos, next_tetromino, placed_blocks, score, level):
    """Draws the window in which the game displays.

    Args:
        window (pygame surface): The full window surface, which contains the
            play area, the score area, and the next piece area.
        play_area (pygame surface): The play area in which falling Tetrominos
            and the already placed blocks are contained.
        score_area (pygame surface): The surface used to display the current
            score and level.
        next_piece (pygame surface): The surface used to display the next
            Tetromino that will fall.
        tetrominos (list): A list of Tetrominos currently in the "bag."
            This list will repopulate once it only contains two items.
        next_tetromino (Tetromino): A Tetromino object of the next Tetromino
            that will fall.
        placed_blocks (list): A list containing the pygame rectangles
            for every block already placed on the level from pieces that
            have already fallen and become fixed in place, but haven't been
            cleared by completing a row.
        score (int): The player's current score.
        level (int): The level that the player is currently on.
    """
    window.fill(BACKGROUND_COLOR)

    next_border_rect = pygame.Rect(
        (PLAY_AREA_WIDTH + 65, 45), (NEXT_PIECE_SIZE + 10, NEXT_PIECE_SIZE + 10))
    pygame.draw.rect(window, TEXT_COLOR, next_border_rect)
    window.blit(next_piece, (PLAY_AREA_WIDTH + 70, 50))
    score_border_rect = pygame.Rect(
        (PLAY_AREA_WIDTH + 35, 100 + NEXT_PIECE_SIZE), (SCORE_WIDTH + 10, SCORE_HEIGHT + 10))
    pygame.draw.rect(window, TEXT_COLOR, score_border_rect)
    window.blit(score_area, (PLAY_AREA_WIDTH + 40, 105 + NEXT_PIECE_SIZE))

    score_area.fill(BANNER_COLOR)
    score_text = STAT_FONT.render(f"Score: {score}", 1, TEXT_COLOR)
    level_text = STAT_FONT.render(f"Level: {level}", 1, TEXT_COLOR)
    score_area.blit(score_text, (10, 10))
    score_area.blit(level_text, (10, SCORE_HEIGHT -
                                 10 - level_text.get_height()))

    next_piece.fill(BANNER_COLOR)
    next_tetromino[0].bounding_box.center = (90, 90)
    next_tetromino[0].draw(next_piece)

    play_border_rect = pygame.Rect(
        (10, 10), (PLAY_AREA_WIDTH + 10, PLAY_AREA_HEIGHT + 10))
    pygame.draw.rect(window, TEXT_COLOR, play_border_rect)
    window.blit(play_area, (15, 15))
    play_area.fill(BANNER_COLOR)
    tetrominos[0].draw(play_area)

    for block in placed_blocks:
        pygame.draw.rect(play_area, block[1], block[0])
    draw_grid(play_area)
    pygame.display.update()


def draw_grid(play_area):
    """Draws a grid onto the play area so the player can see the rows and 
    columns that constrain the Tetrominos.

    Args:
        play_area (pygame surface): The play area in which falling Tetrominos
            and the already placed blocks are contained.
    """
    for x in range(0, PLAY_AREA_WIDTH, GRID_SIZE):
        pygame.draw.line(play_area, GRID_COLOR,
                         (x, 0), (x, PLAY_AREA_HEIGHT), 1)
    for y in range(0, PLAY_AREA_HEIGHT, GRID_SIZE):
        pygame.draw.line(play_area, GRID_COLOR,
                         (0, y), (PLAY_AREA_WIDTH, y), 1)


def pause(window):
    """Pauses the game until it is unpaused by pressing ESC for F1.

    Args:
        window (pygame surface): The window in which the game is being played.
    """
    paused = True
    pause_surface = pygame.Surface(
        (PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
    pause_surface.fill(PAUSE_COLOR)
    pause_text = STAT_FONT.render("GAME PAUSED", 1, TEXT_COLOR)
    pause_surface.blit(
        pause_text,
        (int(PLAY_AREA_WIDTH / 2 - pause_text.get_width() / 2),
         int(PLAY_AREA_HEIGHT / 2 - pause_text.get_height() / 2))
    )
    window.blit(pause_surface, (15, 15))
    pygame.display.update()
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_F1:
                    paused = False


def game_over(window):
    """Ends the game and gives the user a game over screen if they lose,
    with the option to play a new game.

    Args:
        window (pygame surface): The window in which the game is being played.
    """
    paused = True
    game_over_screen = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    game_over_screen.fill(PAUSE_COLOR)
    window.blit(game_over_screen, (0, 0))
    text = ["Game Over", "Press ESC or F1 to quit,",
            "or press any other key to play again."]
    for i, phrase in enumerate(text):
        game_over_text = STAT_FONT.render(phrase, 1, TEXT_COLOR)
        text_rect = game_over_text.get_rect()
        pygame.draw.rect(window, BACKGROUND_COLOR, text_rect)
        window.blit(
            game_over_text,
            (WINDOW_WIDTH / 2 - game_over_text.get_width() / 2,
             WINDOW_HEIGHT / 2 + (i - 1) * 40)
        )

    pygame.display.update()
    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_F1:
                    pygame.quit()
                    quit()
                else:
                    paused = False


def check_lines(placed_blocks):
    """Checks to see if the placed blocks create a full row.

    Args:
        placed_blocks (list): A list containing the pygame rectangles
            for every block already placed on the level from pieces that
            have already fallen and become fixed in place, but haven't been
            cleared by completing a row.

    Returns:
        placed_blocks (list): A list containing the pygame rectangles
            for every block already placed on the level from pieces that
            have already fallen and become fixed in place, but haven't been
            cleared by completing a row.
        rows_cleared (int): The number of rows that were cleared during the
            calling of this function.
    """
    rows_cleared = 0
    blocks_to_clear = []
    blocks_to_move = []
    for y in range(PLAY_AREA_HEIGHT, 0, -GRID_SIZE):
        blocks_in_row = []
        for x in range(0, PLAY_AREA_WIDTH, GRID_SIZE):
            for block in placed_blocks:
                if block[0].left == x and block[0].bottom == y:
                    blocks_in_row.append(block)
        if len(blocks_in_row) == PLAY_AREA_WIDTH / GRID_SIZE:
            for block in blocks_in_row:
                blocks_to_clear.append(block)
            for block in placed_blocks:
                if block[0].bottom <= y:
                    blocks_to_move.append(block)
            rows_cleared += 1
    for block in blocks_to_clear:
        placed_blocks.remove(block)
    for block in blocks_to_move:
        block[0].bottom += GRID_SIZE
    return placed_blocks, rows_cleared


def get_score(rows_cleared, level):
    """Returns a value to add to the score after a row has been cleared.

    Args:
        rows_cleared (int): The number of rows cleared the last time the
            check_lines function was called.
        level (int): The player's current level.

    Returns:
        int: A number of points to be added to the score based on the
            number of rows cleared and the current level.
    """
    if rows_cleared == 0:
        return 0
    elif rows_cleared == 1:
        return 100 * level
    elif rows_cleared == 2:
        return 300 * level
    elif rows_cleared == 3:
        return 500 * level
    elif rows_cleared == 4:
        return 800 * level


def main():
    """The main game loop function.
    """
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetros")
    play_area = pygame.Surface((PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT))
    score_area = pygame.Surface((SCORE_WIDTH, SCORE_HEIGHT))
    next_piece = pygame.Surface((NEXT_PIECE_SIZE, NEXT_PIECE_SIZE))

    clock = pygame.time.Clock()
    score = 0
    level_progress = 0
    level = 1
    tetrominos = []
    placed_blocks = []

    restart_game = False
    run = True

    while run:
        clock.tick(30)

        if len(tetrominos) < 2:
            shapes = list(SHAPES)
            random.shuffle(shapes)
            for shape in shapes:
                tetrominos.append(Tetromino(shape))

        tetrominos[0].fall(level)
        next_tetromino = [tetrominos[1].deepcopy()]
        draw_window(window, play_area, score_area, next_piece,
                    tetrominos, next_tetromino, placed_blocks, score, level)

        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == KEYDOWN:
                if event.key in [K_UP, K_x, K_KP1, K_KP5, K_KP9]:
                    tetrominos[0].rotate()
                if event.key in [K_z, K_LCTRL, K_RCTRL, K_KP3, K_KP7]:
                    tetrominos[0].rotate_cc()
                if event.key in [K_SPACE, K_DOWN, K_KP2, K_KP8]:
                    tetrominos[0].drop(placed_blocks)
                if event.key in [K_LSHIFT, K_RSHIFT, K_c, K_KP0]:
                    tetrominos[0].falling = False
                if event.key in [K_ESCAPE, K_F1]:
                    pause(window)
                if event.key in [K_LEFT, K_KP4]:
                    tetrominos[0].shift("left", placed_blocks)
                if event.key in [K_RIGHT, K_KP6]:
                    tetrominos[0].shift("right", placed_blocks)

            if event.type == KEYUP:
                if event.key in [K_LSHIFT, K_RSHIFT, K_c, K_KP0]:
                    tetrominos[0].falling = True

        for square in tetrominos[0].squares:
            if square.left < 0:
                tetrominos[0].bounding_box.left += GRID_SIZE
            elif square.right > PLAY_AREA_WIDTH:
                tetrominos[0].bounding_box.right -= GRID_SIZE

        if placed_blocks:
            for block in placed_blocks:
                try:
                    for square in tetrominos[0].squares:
                        if square.bottom == block[0].top and square.left == block[0].left:
                            for x in range(len(tetrominos[0].blocks)):
                                for y in range(len(tetrominos[0].blocks)):
                                    if tetrominos[0].blocks[y][x]:
                                        placed_blocks.append((pygame.Rect(
                                            (tetrominos[0].bounding_box.left +
                                             GRID_SIZE * x),
                                            (tetrominos[0].bounding_box.top +
                                             GRID_SIZE * y),
                                            GRID_SIZE,
                                            GRID_SIZE
                                        ), tetrominos[0].color))
                            tetrominos.pop(0)
                            break
                except:
                    pass
                if block[0].top < 0:
                    game_over(window)
                    restart_game = True
                    break

        if restart_game == True:
            score = 0
            level = 1
            tetrominos = []
            placed_blocks = []
            restart_game = False
            continue

        try:
            for square in tetrominos[0].squares:
                if square.bottom == PLAY_AREA_HEIGHT:
                    for x in range(len(tetrominos[0].blocks)):
                        for y in range(len(tetrominos[0].blocks)):
                            if tetrominos[0].blocks[y][x]:
                                placed_blocks.append((pygame.Rect(
                                    (tetrominos[0].bounding_box.left +
                                     GRID_SIZE * x),
                                    (tetrominos[0].bounding_box.top +
                                     GRID_SIZE * y),
                                    GRID_SIZE,
                                    GRID_SIZE
                                ), tetrominos[0].color))
                    tetrominos.pop(0)
                    break
        except:
            continue

        placed_blocks, rows_cleared = check_lines(placed_blocks)
        score += get_score(rows_cleared, level)
        level_progress += rows_cleared

        if level_progress == 10:
            level_progress = 0
            level += 1


if __name__ == "__main__":
    main()
