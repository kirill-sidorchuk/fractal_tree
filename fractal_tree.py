"""
Builds fractal tree
"""
from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np

ROOF_HEIGHT_FACTOR = 0.33
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800


@dataclass
class TreeElement:
    """
    Represents a tree element
    """
    polygon: List[Tuple[float, float]]  # contains 7 points, the last three are the start of the next 2 branches
    depth: int  # depth of the element in the tree


def create_new_element(a: Tuple[float, float], b: Tuple[float, float], depth: int) -> TreeElement:
    """
    Creates a new tree element with the base given by a and b

    :param a: start point of the base
    :param b: end point of the base
    :param depth: depth of the element in the tree
    :return: a new tree element
    """

    # base axis
    ba_x = b[0] - a[0]
    ba_y = b[1] - a[1]

    # tangential axis
    ta_x = -ba_y
    ta_y = ba_x

    # "roof" height
    base_length = (ta_x ** 2 + ta_y ** 2) ** 0.5
    rh = base_length * ROOF_HEIGHT_FACTOR

    # "roof top" point
    rt_x = a[0] + ta_x + ba_x * 0.5 + rh * ta_x / base_length
    rt_y = a[1] + ta_y + ba_y * 0.5 + rh * ta_y / base_length

    points = [
        (a[0] + ta_x, a[1] + ta_y),
        a,
        b,
        (b[0] + ta_x, b[1] + ta_y),
        (a[0] + ta_x, a[1] + ta_y),
        (rt_x, rt_y),
        (b[0] + ta_x, b[1] + ta_y)
    ]
    return TreeElement(polygon=points, depth=depth)


def create_tree(a: Tuple[float, float], b: Tuple[float, float], max_depth: int) -> List[TreeElement]:
    """
    Creates a tree with the base given by a and b

    :param a: start point of the base
    :param b: end point of the base
    :param max_depth: maximum depth of the tree
    :return: a list of tree elements
    """

    all_elements = []

    # creating "front" list. It will contain all bases that needs to be expanded
    # the list will work in FIFO mode
    front = [(a, b, 0)]  # (a, b, depth)

    while len(front) != 0:
        # pop head and create new element
        base_a, base_b, depth = front.pop(0)
        element = create_new_element(base_a, base_b, depth)
        all_elements.append(element)

        # check if we reached the maximum depth
        if depth >= max_depth:
            continue

        # expand the base and add new bases to the front list (at the end of the list)
        a1 = element.polygon[-3]
        b1 = element.polygon[-2]
        a2 = element.polygon[-2]
        b2 = element.polygon[-1]

        front.append((a1, b1, depth + 1))
        front.append((a2, b2, depth + 1))

    return all_elements


def main():
    """
    Main function
    """

    # create a black image
    img = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), np.uint8)

    # create first base at the top of the image
    first_base_width = 220
    a = (CANVAS_WIDTH / 2 - first_base_width / 2, 0)
    b = (CANVAS_WIDTH / 2 + first_base_width / 2, 0)

    # create all elements up to the depth of 12
    all_elements = create_tree(a, b, 12)

    # draw all elements as wireframe with antialiasing
    for element in all_elements:
        polygon = np.array(element.polygon, np.int32)
        polygon = polygon.reshape((-1, 1, 2))
        cv2.polylines(img, [polygon], False, (50, 200, 100), 1, cv2.LINE_AA)

    # show the image
    cv2.imshow('Fractal Tree', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
