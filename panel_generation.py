import numpy as np
import pygame
import sys
from algo import generate_pattern

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
BRICK_SIZE = 50
BRICK_BORDER_WIDTH = 2
MOVE_THRESHOLD = 10

# Panel configuration
nrows = 14
ncols = 10
max_dul = 4

# Color mapping for bricks
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

# Initialize pygame
pygame.init()

# Set up the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('砖块矩阵展示')


class Panel:
    def __init__(self, rows, cols, max_dul):
        self.rows = rows
        self.cols = cols
        self.max_dul = max_dul
        self.panel = generate_pattern(rows, cols, max_dul)
        self.panel_x = (WINDOW_WIDTH - self.cols * BRICK_SIZE) // 2
        self.panel_y = (WINDOW_HEIGHT - self.rows * BRICK_SIZE) // 2
        self.bricks = self.create_bricks()

    def create_bricks(self):
        bricks = []
        for row in range(self.rows):
            brick_row = []
            for col in range(self.cols):
                brick_value = self.panel[row][col]
                x = self.panel_x + col * BRICK_SIZE
                y = self.panel_y + row * BRICK_SIZE
                brick_row.append(Brick(x, y, row, col, brick_value, self))
            bricks.append(brick_row)
        return bricks

    def move_brick(self, brick, new_row, new_col):
        if self.bricks[new_row][new_col] is None:
            self.bricks[brick.row_idx][brick.col_idx] = None
            brick.row_idx, brick.col_idx = new_row, new_col
            brick.x = self.panel_x + new_col * BRICK_SIZE
            brick.y = self.panel_y + new_row * BRICK_SIZE
            self.bricks[new_row][new_col] = brick

    def delete_brick(self, row, col):
        self.bricks[row][col] = None

    def pos_to_brick(self, x, y):
        col = (x - self.panel_x) // BRICK_SIZE
        row = (y - self.panel_y) // BRICK_SIZE

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.bricks[row][col]
        return None

    def pos_to_index(self, x, y):
        col = (x - self.panel_x) // BRICK_SIZE
        row = (y - self.panel_y) // BRICK_SIZE

        return row, col

    def get_neighbor(self, brick):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
        neighbors = []
        for dx, dy in directions:
            neighbor = None
            distance = 1
            while True:
                nx, ny = brick.row_idx + dx * distance, brick.col_idx + dy * distance
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if self.bricks[nx][ny] is not None:
                        neighbor = self.bricks[nx][ny]
                        break
                else:
                    break
                distance += 1
            neighbors.append(neighbor)
        return neighbors

    def refresh_panel(self):
        for row in self.bricks:
            for brick in row:
                if brick is not None:
                    brick.draw()


class Brick:
    def __init__(self, x, y, idx, idy, brick_value, panel):
        self.x = x
        self.y = y
        self.row_idx = idx
        self.col_idx = idy
        self.color = color_map.get(brick_value, pygame.Color('gray'))
        self.brick_value = brick_value
        self.original_x = x
        self.original_y = y
        self.dragging = False
        self.lock_direction = None
        self.direction = None
        self.panel = panel
        self.left = None
        self.right = None
        self.top = None
        self.down = None
        self.selected = False

    def draw(self):
        pygame.draw.rect(window, self.color, (self.x, self.y, BRICK_SIZE, BRICK_SIZE))
        pygame.draw.rect(window, pygame.Color('black'), (self.x, self.y, BRICK_SIZE, BRICK_BORDER_WIDTH))
        pygame.draw.rect(window, pygame.Color('black'), (self.x, self.y, BRICK_BORDER_WIDTH, BRICK_SIZE))
        pygame.draw.rect(window, pygame.Color('black'),
                         (self.x, self.y + BRICK_SIZE - BRICK_BORDER_WIDTH, BRICK_SIZE, BRICK_BORDER_WIDTH))
        pygame.draw.rect(window, pygame.Color('black'),
                         (self.x + BRICK_SIZE - BRICK_BORDER_WIDTH, self.y, BRICK_BORDER_WIDTH, BRICK_SIZE))

        font = pygame.font.Font(None, 30)
        text_surface = font.render(self.brick_value, True, pygame.Color('white'))
        text_rect = text_surface.get_rect(center=(self.x + BRICK_SIZE // 2, self.y + BRICK_SIZE // 2))
        window.blit(text_surface, text_rect)

    def get_top(self):
        return self.x, self.y

    def get_bot(self):
        return self.x + BRICK_SIZE, self.y + BRICK_SIZE

    def move(self, mouse_x, mouse_y):
        if self.dragging:
            if self.lock_direction is None:
                if abs(mouse_x - self.original_x) > abs(mouse_y - self.original_y):
                    self.lock_direction = 'x'
                else:
                    self.lock_direction = 'y'

            if self.lock_direction == 'x':
                new_x = mouse_x - BRICK_SIZE // 2
                [min_x, max_x, min_y, max_y] = self.get_exe_pose()
                self.x = np.clip(new_x, min_x, max_x)
            elif self.lock_direction == 'y':
                new_y = mouse_y - BRICK_SIZE // 2
                [min_x, max_x, min_y, max_y] = self.get_exe_pose()
                self.y = np.clip(new_y, min_y, max_y)

    def release(self):
        self.dragging = False
        self.lock_direction = None

        # Check neighbors for same value and delete
        neighbors = self.panel.get_neighbor(self)
        for n in neighbors:
            print(None if n is None else n.brick_value)

        for neighbor in neighbors:
            if neighbor is None:
                continue
            if neighbor.brick_value == self.brick_value:
                self.panel.delete_brick(self.row_idx, self.col_idx)
                self.panel.delete_brick(neighbor.row_idx, neighbor.col_idx)
                return True
        return False

    def reset_position(self):
        ori_row, ori_col = self.panel.pos_to_index(self.original_x, self.original_y)
        self.panel.move_brick(self, ori_row, ori_col)

    def get_exe_pose(self, width=BRICK_SIZE, height=BRICK_SIZE):
        [top, down, left, right] = self.panel.get_neighbor(self)
        min_x = self.panel.panel_x if left is None else left.x + width
        max_x = self.panel.panel_x + (self.panel.cols - 1) * BRICK_SIZE if right is None else right.x - width
        min_y = self.panel.panel_y if top is None else top.y + height
        max_y = self.panel.panel_y + (self.panel.rows - 1) * BRICK_SIZE if down is None else down.y - width
        return min_x, max_x, min_y, max_y


def round_to_nearest_50(num):
    quotient = num // 50
    remainder = num % 50

    if remainder >= 25:
        rounded_num = (quotient + 1) * 50
    else:
        rounded_num = quotient * 50

    return rounded_num


def main():
    panel = Panel(nrows, ncols, max_dul)
    dragging_brick = None  # Temporary variable to store the dragging brick

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    row, col = (mouse_y - panel.panel_y) // BRICK_SIZE, (mouse_x - panel.panel_x) // BRICK_SIZE
                    dragging_brick = panel.bricks[row][col]
                    if not dragging_brick is None:
                        dragging_brick.dragging = True
                        dragging_brick.original_x = dragging_brick.x
                        dragging_brick.original_y = dragging_brick.y
                    if dragging_brick:
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_brick is not None:
                    round_x, round_y = round_to_nearest_50(dragging_brick.x), round_to_nearest_50(dragging_brick.y)
                    row, col = panel.pos_to_index(round_x, round_y)
                    ori_row, ori_col = dragging_brick.row_idx, dragging_brick.col_idx

                    if row != ori_row or col != ori_col:
                        print("Before move dragging brick x: {}; y: {}".format(ori_col, ori_row))
                        panel.move_brick(dragging_brick, row, col)
                        print("Before move dragging brick x: {}; y: {}".format(dragging_brick.col_idx, dragging_brick.row_idx))
                    statu = dragging_brick.release()

                    if not statu:
                        dragging_brick.reset_position()
                    else:
                        print("Limitation")
                        panel.delete_brick(ori_row, ori_col)
                    dragging_brick = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_brick is not None:
                    mouse_x, mouse_y = event.pos
                    dragging_brick.move(mouse_x, mouse_y)

        window.fill(pygame.Color('black'))

        panel.refresh_panel()

        pygame.display.flip()


if __name__ == '__main__':
    main()
