import numpy as np
import string
import random
LETTERS = list(string.ascii_uppercase)

EX_LETTERS = LETTERS + ['!',"@","#","$","%","&","?","<",">","+","-","~"]


def transform_dict_to_list(input_dict):
    result_list = []

    for key, value in input_dict.items():
        transformed_key = key * 2  # 将每个键乘以2
        transformed_values = [transformed_key] * value  # 复制值个数次

        result_list.extend(transformed_values)  # 将处理后的值扩展到结果列表中

    return result_list

def min_number_pair_types(n, k):
    if k <= 0 or n <= 0 or n % 2 != 0:
        return -1  # Invalid input

    count = 0
    while n > 0:
        count += 1
        n -= 2 * k  # 每种数对最多出现 k 次，数对的和是 2 倍的 k

    return count

def generate_category_counts(categories, max_repeats, total_count):
    # 初始化结果字典，所有类别初始数量为1，以确保每个值都大于零
    result = {category: 1 for category in categories}

    remaining_count = total_count - len(categories)  # 初始剩余数量

    # 循环，直到剩余数量为0
    while remaining_count > 0:
        # 随机选择一个类别，并增加它的计数
        category = random.choice(categories)

        # 计算该类别可以增加的最大值
        max_increment = min(max_repeats - result[category], remaining_count)

        if max_increment > 0:
            increment = random.randint(1, max_increment)
            result[category] += increment
            remaining_count -= increment

    return result

def generate_pattern(rows, cols, max_dul=3):
    assert rows%2 == 0 and cols%2 == 0, "Error! Either Cols or rows are not even number"
    total_num = rows*cols
    min_int,max_int = np.ceil(total_num/2/max_dul), min((total_num/2), len(LETTERS))
    types = random.randint(min_int, max_int)
    print(f"Select {types} types of bricks")
    C_LETTERS = np.random.choice(a=LETTERS, size=types, replace=False)
    results = generate_category_counts(
        categories=C_LETTERS,max_repeats=max_dul, total_count=total_num//2
    )

    result = transform_brick(results, rows, cols)
    return result

def transform_brick(brick_dict,rows,cols):
    total_number = sum(brick_dict.values())*2
    brick_list = []

    for k,v in brick_dict.items():
        pair = [k]*2*v
        brick_list.extend(pair)
    brick_list = np.array(brick_list)
    np.random.shuffle(brick_list)
    brick_list = brick_list.reshape(rows, cols)
    return brick_list


def determine_direction(dx, dy):
    """
    Determines the direction of the mouse movement based on dx and dy.
    Returns 'left', 'right', 'up', or 'down'.
    """
    if abs(dx) > abs(dy):
        return 'right' if dx > 0 else 'left'
    else:
        return 'down' if dy > 0 else 'up'


def same_direction_group(dir1, dir2):
    # 判断两个方向是否都属于同一组 (up, down) 或者 (left, right)
    if (dir1 in ['up', 'down'] and dir2 in ['up', 'down']) or (dir1 in ['left', 'right'] and dir2 in ['left', 'right']):
        return True
    else:
        return False

if __name__ == '__main__':
    x = 10

    for i in range(x,20):
        print(i)