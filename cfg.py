import pygame

background_pic = r""

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
BRICK_SIZE = 50
BRICK_BORDER_WIDTH = 2
MOVE_THRESHOLD = 10

nrows = 8
ncols = 8
max_dul = 2

color_map = {
    'A': pygame.Color('red'),
    'B': pygame.Color('green'),
    'C': pygame.Color('blue'),
    'D': pygame.Color('orange'),
    'E': pygame.Color('yellow'),
    'F': pygame.Color('purple'),
    'G': pygame.Color('cyan'),
    'H': pygame.Color('pink'),
    'I': pygame.Color('teal'),
    'J': pygame.Color('brown'),
    'K': pygame.Color('lightblue'),
    'L': pygame.Color('lightgreen'),
    'M': pygame.Color('lightcoral'),
    'N': pygame.Color('lightsalmon'),
    'O': pygame.Color('lightpink'),
    'P': pygame.Color('lightgray'),
    'Q': pygame.Color('darkred'),
    'R': pygame.Color('darkgreen'),
    'S': pygame.Color('darkblue'),
    'T': pygame.Color('darkorange'),
    'U': pygame.Color('darkcyan'),
    'V': pygame.Color('darkmagenta'),
    'W': pygame.Color('darkviolet'),
    'X': pygame.Color('indianred'),
    'Y': pygame.Color('sienna'),
    'Z': pygame.Color('slateblue')
}