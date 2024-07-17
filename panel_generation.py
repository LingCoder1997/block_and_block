import numpy as np
import pygame
import sys
from algo import generate_pattern,determine_direction,same_direction_group
import itertools
from cfg import *

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
        self.dirty_bricks = []
    def get_bot(self):
        return self.panel_y + self.rows*BRICK_SIZE

    def get_right(self):
        return self.panel_x+ self.cols*BRICK_SIZE

    def get_top(self):
        return self.panel_y

    def get_left(self):
        return self.panel_x

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

    def get_same_bricks(self, value):
        temp_bricks = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.bricks[i][j].brick_value == value:
                    temp_bricks.append(self.bricks[i][j])
        return temp_bricks

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

    def get_connect_bricks(self, brick):

        if brick is None:
            return None
        else:
            brick_queue = [brick]
            if brick.direction is None:
                return brick_queue
            elif brick.direction == "up":
                lock_x = brick.col_idx
                if brick.row_idx > 0:
                    for i in range(brick.row_idx-1, -1, -1):
                        if not self.bricks[i][lock_x] is None:
                            brick_queue.append(self.bricks[i][lock_x])
                        else:
                            return brick_queue
                    return brick_queue
                else:
                    return brick_queue
            elif brick.direction == "down":
                lock_x = brick.col_idx
                if brick.row_idx < nrows-1:
                    for i in range(brick.row_idx+1, nrows):
                        if not self.bricks[i][lock_x] is None:
                            brick_queue.append(self.bricks[i][lock_x])
                        else:
                            return brick_queue
                    return brick_queue
                else:
                    return brick_queue

            elif brick.direction == "left":
                lock_y = brick.row_idx
                if brick.col_idx > 0:
                    for j in range(brick.col_idx-1, 0, -1):
                        if not self.bricks[lock_y][j] is None:
                            brick_queue.append(self.bricks[lock_y][j])
                        else:
                            return brick_queue
                    return brick_queue
                else:
                    return brick_queue

            elif brick.direction == "right":
                lock_y = brick.row_idx
                if brick.col_idx < ncols-1:
                    for j in range(brick.col_idx+1, ncols):
                        if not self.bricks[lock_y][j] is None:
                            brick_queue.append(self.bricks[lock_y][j])
                        else:
                            return brick_queue
                    return brick_queue
                else:
                    return brick_queue

            else:
                raise KeyError("Error! Direction {} is not included in the list".format(brick.direction))

    def refresh_panel(self):
        for row in self.bricks:
            for brick in row:
                if brick is not None:
                    brick.draw()

    def check_win(self):
        flat_list = list(itertools.chain(*self.bricks))
        flat_list = list(filter(lambda x : x is not None, flat_list))
        if len(flat_list) == 0:
            print("Game Win!!!")
            return True
        else:
            print("{} bricks left".format(len(flat_list)))
            return False

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
        self.abs_dir = None
        self.prev_mouse_x = None
        self.prev_mouse_y = None

        self.shaking = False
        self.shake_timer = 0
        self.shake_angles = [6, -12, 6]
        self.shake_index = 0

    def draw(self):
        if self.shaking:
            self.shake_timer += 1
            if self.shake_timer < 3:
                angle = self.shake_angles[self.shake_index]
                self.shake_index = (self.shake_index + 1) % len(self.shake_angles)
            else:
                self.shaking = False
                self.shake_timer = 0
                self.shake_index = 0
                angle = 0
        else:
            angle = 0

        # Create the original surface for the brick
        original_surface = pygame.Surface((BRICK_SIZE, BRICK_SIZE), pygame.SRCALPHA)
        original_surface.fill(self.color)

        # Create the font and render the text onto a separate surface
        font = pygame.font.Font(None, 30)
        text_surface = font.render(self.brick_value, True, pygame.Color('white'))

        # Get the rect for the text surface
        text_rect = text_surface.get_rect(center=(BRICK_SIZE // 2, BRICK_SIZE // 2))

        # Blit the text onto the original brick surface
        original_surface.blit(text_surface, text_rect)

        # Rotate the original surface with the text
        rotated_surface = pygame.transform.rotate(original_surface, angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x + BRICK_SIZE // 2, self.y + BRICK_SIZE // 2))

        # Draw the rotated surface
        window.blit(rotated_surface, rotated_rect.topleft)

        # Draw the border
        pygame.draw.rect(window, pygame.Color('black'), (self.x, self.y, BRICK_SIZE, BRICK_BORDER_WIDTH))
        pygame.draw.rect(window, pygame.Color('black'), (self.x, self.y, BRICK_BORDER_WIDTH, BRICK_SIZE))
        pygame.draw.rect(window, pygame.Color('black'),
                         (self.x, self.y + BRICK_SIZE - BRICK_BORDER_WIDTH, BRICK_SIZE, BRICK_BORDER_WIDTH))
        pygame.draw.rect(window, pygame.Color('black'),
                         (self.x + BRICK_SIZE - BRICK_BORDER_WIDTH, self.y, BRICK_BORDER_WIDTH, BRICK_SIZE))

    def shake(self):
        self.shaking = True
        self.shake_timer = 0
        self.shake_index = 0

    def get_top(self):
        return self.x, self.y

    def get_bot(self):
        return self.x + BRICK_SIZE, self.y + BRICK_SIZE

    def move(self, mouse_x, mouse_y):
        if self.dragging:
            if self.prev_mouse_x is not None and self.prev_mouse_y is not None:
                dx = mouse_x - self.prev_mouse_x
                dy = mouse_y - self.prev_mouse_y
                self.direction = determine_direction(dx,dy)
                if self.lock_direction is None:
                    if abs(dx) > abs(dy):
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

            self.prev_mouse_x = mouse_x
            self.prev_mouse_y = mouse_y


    def release(self):
        self.dragging = False
        self.lock_direction = None
        self.prev_mouse_x = None
        self.prev_mouse_y = None

        # Check neighbors for same value and delete
        neighbors = self.panel.get_neighbor(self)

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
        if ori_row == self.row_idx and ori_col == self.col_idx:
            brick_list = self.panel.get_same_bricks(self.brick_value)
            self.x = self.original_x
            self.y = self.original_y
            for b in brick_list:
                b.shake()
        else:
            self.panel.move_brick(self, ori_row, ori_col)

    def get_exe_pose(self, width=BRICK_SIZE, height=BRICK_SIZE):
        [top, down, left, right] = self.panel.get_neighbor(self)
        min_x = self.panel.panel_x if left is None else left.x + width
        max_x = self.panel.panel_x + (self.panel.cols - 1) * BRICK_SIZE if right is None else right.x - width
        min_y = self.panel.panel_y if top is None else top.y + height
        max_y = self.panel.panel_y + (self.panel.rows - 1) * BRICK_SIZE if down is None else down.y - width
        return min_x, max_x, min_y, max_y

class Bricks(Brick):
    def __init__(self, initial_brick):
        super().__init__(initial_brick.x, initial_brick.y, initial_brick.row_idx, initial_brick.col_idx, initial_brick.brick_value, initial_brick.panel)
        self.head = initial_brick
        self.tail = None
        self.bricks = None
        self.pos_reset = True
        self.start_pos = (self.head.row_idx, self.head.col_idx)
        self.ori_pos = []
        self.values = []
        self.ori_dir = None

        self.min_x = -1
        self.max_x = -1
        self.min_y = -1
        self.max_y = -1

    def move(self, mouse_x, mouse_y):
        if self.dragging:
            if self.prev_mouse_x is not None and self.prev_mouse_y is not None:
                dx = mouse_x - self.prev_mouse_x
                dy = mouse_y - self.prev_mouse_y
                if self.direction is None:
                    self.direction = determine_direction(dx,dy)
                    self.ori_dir = determine_direction(dx,dy)
                elif same_direction_group(self.direction, determine_direction(dx,dy)):
                    self.direction = determine_direction(dx,dy)

                if self.pos_reset:
                    self._init_queue()
                if self.head.x != self.original_x or self.head.y != self.original_y:
                    self.pos_reset = False

                if self.lock_direction is None:
                    if abs(dx) > abs(dy):
                        self.lock_direction = 'x'
                    else:
                        self.lock_direction = 'y'

                    for brick in self.bricks:
                        brick.lock_direction = self.lock_direction
                        brick.direction = self.direction

                if self.direction in ['left', 'right']:
                    temp_x = self.head.x + dx
                    new_x = np.clip(temp_x, self.min_x, self.max_x)
                    act_dx = new_x - self.head.x
                    for brick in self.bricks:
                        brick.x += act_dx
                elif self.direction in ['up', 'down']:
                    temp_y = self.head.y + dy
                    new_y = np.clip(temp_y, self.min_y, self.max_y)
                    act_dy = new_y - self.head.y
                    for brick in self.bricks:
                        brick.y += act_dy
                else:
                    raise KeyError("Error! The direction key {} is not found!".format(self.direction))
            self.prev_mouse_x = mouse_x
            self.prev_mouse_y = mouse_y

    def get_exe_pose(self, width=BRICK_SIZE, height=BRICK_SIZE):
        [top_2, down_2, left_2, right_2] = self.panel.get_neighbor(self.tail)
        if self.direction == "up":
            dy = (self.panel.get_top() if top_2 is None else top_2.y+BRICK_SIZE) - self.tail.y
            min_x = self.head.x
            max_x = self.head.x
            min_y = self.head.y + dy
            max_y = self.head.y
        elif self.direction == "down":
            dy = (self.panel.get_bot() if down_2 is None else down_2.y) - self.tail.y - BRICK_SIZE
            min_x = self.head.x
            max_x = self.head.x
            min_y = self.head.y
            max_y = self.head.y + dy
        elif self.direction == "left":
            dx = (self.panel.get_left() if left_2 is None else left_2.x+BRICK_SIZE) - self.tail.x
            min_x = self.head.x + dx
            max_x = self.head.x
            min_y = self.head.y
            max_y = self.head.y
        elif self.direction == "right":
            dx = (self.panel.get_right() if right_2 is None else right_2.x) - (self.tail.x + BRICK_SIZE)
            min_x = self.head.x
            max_x = self.head.x + dx
            min_y = self.head.y
            max_y = self.head.y
        else:
            raise KeyError("Error! The direction {} is not mentioned!".format(self.direction))
        return round_to_nearest_50(min_x), round_to_nearest_50(max_x), round_to_nearest_50(min_y), round_to_nearest_50(max_y)

    def _init_queue(self):
        self.head.direction = self.direction
        self.bricks = self.panel.get_connect_bricks(self.head)
        self.tail = self.bricks[-1]
        self.ori_pos = [(b.original_x,b.original_y) for b in self.bricks]
        self.values = [b.brick_value for b in self.bricks]
        self.min_x, self.max_x, self.min_y, self.max_y = self.get_exe_pose()
    def release(self):
        for brick in self.bricks:
            brick.dragging = False
            brick.lock_direction = None
            brick.prev_mouse_x = None
            brick.prev_mouse_y = None

        neighbors = self.panel.get_neighbor(self.head)
        for neighbor in neighbors:
            if neighbor is None:
                continue
            if neighbor.brick_value == self.head.brick_value:
                self.panel.delete_brick(self.head.row_idx, self.head.col_idx)
                self.panel.delete_brick(neighbor.row_idx, neighbor.col_idx)
                self.bricks.pop(0)
                return True
        return False

    def reset_position(self):
        for brick in self.bricks:
            brick.reset_position()


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
    dragging_bricks = None
    lock = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    row, col = (mouse_y - panel.panel_y) // BRICK_SIZE, (mouse_x - panel.panel_x) // BRICK_SIZE
                    if 0 <= row < panel.rows and 0 <= col < panel.cols:
                        dragging_brick = panel.bricks[row][col]
                    else:
                        break
                    if not dragging_brick is None:
                        dragging_brick.dragging = True
                        dragging_brick.original_x = dragging_brick.x
                        dragging_brick.original_y = dragging_brick.y
                    if dragging_brick:
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_brick is not None:
                    if dragging_bricks is None:
                        round_x, round_y = round_to_nearest_50(dragging_brick.x), round_to_nearest_50(dragging_brick.y)
                        row, col = panel.pos_to_index(round_x, round_y)
                        ori_row, ori_col = dragging_brick.row_idx, dragging_brick.col_idx

                        if row != ori_row or col != ori_col:
                            panel.move_brick(dragging_brick, row, col)
                        statu = dragging_brick.release()

                        if not statu:
                            dragging_brick.reset_position()
                        else:
                            panel.delete_brick(row,col)
                        dragging_brick = None
                    else:
                        if dragging_bricks.bricks is None:
                            break
                        for brick in reversed(dragging_bricks.bricks):
                            round_x, round_y = round_to_nearest_50(brick.x), round_to_nearest_50(
                                brick.y)
                            row, col = panel.pos_to_index(round_x, round_y)
                            ori_row, ori_col = brick.row_idx, brick.col_idx

                            if row != ori_row or col != ori_col:
                                panel.move_brick(brick, row, col)

                        statu = dragging_bricks.release()
                        if not statu:
                            dragging_bricks.reset_position()

                        dragging_brick = None
                        dragging_bricks = None
                        lock = False
                if panel.check_win():
                    pygame.quit()
                    sys.exit()


            elif event.type == pygame.MOUSEMOTION:
                if dragging_brick is not None:
                    mouse_x, mouse_y = event.pos
                    if not lock:
                        dragging_bricks = Bricks(dragging_brick)
                        dragging_bricks.dragging = True
                        lock = True

                    dragging_bricks.move(mouse_x, mouse_y)

        window.fill(pygame.Color('black'))

        panel.refresh_panel()

        pygame.display.flip()


if __name__ == '__main__':
    main()
