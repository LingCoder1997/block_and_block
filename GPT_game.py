import pygame
import sys
import random

# 初始化 Pygame
pygame.init()

# 屏幕大小和其他常量
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
GRID_SIZE = 4
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE
TILE_PADDING = 10
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# 初始化屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("砖了个砖")

# 初始化网格
grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

def add_new_tile():
    empty_tiles = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if not empty_tiles:
        return
    r, c = random.choice(empty_tiles)
    grid[r][c] = random.choice([2, 4])

def draw_grid():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            color = TILE_COLORS.get(value, TILE_COLORS[2048])
            rect = pygame.Rect(c * TILE_SIZE + TILE_PADDING, r * TILE_SIZE + TILE_PADDING,
                               TILE_SIZE - TILE_PADDING * 2, TILE_SIZE - TILE_PADDING * 2)
            pygame.draw.rect(screen, color, rect)
            if value:
                font = pygame.font.Font(None, 36)
                text = font.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def move_left():
    moved = False
    for r in range(GRID_SIZE):
        row = [value for value in grid[r] if value != 0]
        merged_row = []
        skip = False
        for i in range(len(row)):
            if skip:
                skip = False
                continue
            if i + 1 < len(row) and row[i] == row[i + 1]:
                merged_row.append(row[i] * 2)
                skip = True
                moved = True
            else:
                merged_row.append(row[i])
        merged_row += [0] * (GRID_SIZE - len(merged_row))
        if merged_row != grid[r]:
            moved = True
        grid[r] = merged_row
    return moved

def move_right():
    moved = False
    for r in range(GRID_SIZE):
        row = [value for value in grid[r] if value != 0]
        merged_row = []
        skip = False
        for i in range(len(row) - 1, -1, -1):
            if skip:
                skip = False
                continue
            if i - 1 >= 0 and row[i] == row[i - 1]:
                merged_row.insert(0, row[i] * 2)
                skip = True
                moved = True
            else:
                merged_row.insert(0, row[i])
        merged_row = [0] * (GRID_SIZE - len(merged_row)) + merged_row
        if merged_row != grid[r]:
            moved = True
        grid[r] = merged_row
    return moved

def move_up():
    moved = False
    for c in range(GRID_SIZE):
        column = [grid[r][c] for r in range(GRID_SIZE) if grid[r][c] != 0]
        merged_column = []
        skip = False
        for i in range(len(column)):
            if skip:
                skip = False
                continue
            if i + 1 < len(column) and column[i] == column[i + 1]:
                merged_column.append(column[i] * 2)
                skip = True
                moved = True
            else:
                merged_column.append(column[i])
        merged_column += [0] * (GRID_SIZE - len(merged_column))
        for r in range(GRID_SIZE):
            if grid[r][c] != merged_column[r]:
                moved = True
            grid[r][c] = merged_column[r]
    return moved

def move_down():
    moved = False
    for c in range(GRID_SIZE):
        column = [grid[r][c] for r in range(GRID_SIZE) if grid[r][c] != 0]
        merged_column = []
        skip = False
        for i in range(len(column) - 1, -1, -1):
            if skip:
                skip = False
                continue
            if i - 1 >= 0 and column[i] == column[i - 1]:
                merged_column.insert(0, column[i] * 2)
                skip = True
                moved = True
            else:
                merged_column.insert(0, column[i])
        merged_column = [0] * (GRID_SIZE - len(merged_column)) + merged_column
        for r in range(GRID_SIZE):
            if grid[r][c] != merged_column[r]:
                moved = True
            grid[r][c] = merged_column[r]
    return moved

def check_game_over():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return False
            if r + 1 < GRID_SIZE and grid[r][c] == grid[r + 1][c]:
                return False
            if c + 1 < GRID_SIZE and grid[r][c] == grid[r][c + 1]:
                return False
    return True

# 添加初始的两个砖块
add_new_tile()
add_new_tile()

# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            moved = False
            if event.key == pygame.K_LEFT:
                moved = move_left()
            elif event.key == pygame.K_RIGHT:
                moved = move_right()
            elif event.key == pygame.K_UP:
                moved = move_up()
            elif event.key == pygame.K_DOWN:
                moved = move_down()
            if moved:
                add_new_tile()
            if check_game_over():
                print("Game Over")
                pygame.quit()
                sys.exit()

    screen.fill(BACKGROUND_COLOR)
    draw_grid()
    pygame.display.flip()
