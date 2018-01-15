import math
from mozlog.structured import get_proxy_logger


LOG = get_proxy_logger("windowController")

def pixel_color_is_similar(input_pixel_a, input_pixel_b, threshold=45, channel_number=3):
    """
    compare two pixel color similarity
    :param input_pixel_a:
    :param input_pixel_b:
    :param threshold:
    :param channel_number:
    :return:
    """
    is_similar = True
    sum = 0
    for channel_index in xrange(channel_number):
        delta = abs(input_pixel_a[channel_index] - input_pixel_b[channel_index])
        sum += delta
        if delta > threshold:
            is_similar = False
    if sum > threshold:
        is_similar = False
    return is_similar


def find_image_viewport(input_img_grab_obj):
    """
    find the image viewport (default will look into the white background space)
    :param input_rgb_pixels:
    :return: {"x": value, "y": value, "width": value, "height": value}
    """

    left, right, top, bottom = (None, ) * 4
    viewport = None

    # init image variables
    input_img_size = input_img_grab_obj.size
    input_img_rgb_pixels = input_img_grab_obj.convert("RGB").load()

    # init image startup x, y, width, height
    width, height = input_img_size
    x = int(math.floor(width / 2))
    y = int(math.floor(height / 2))

    # set white color as target background color
    background_rgb = (255, 255, 255)

    # Find the left edge
    for current_x in range(int(math.floor(width / 2)), -1, -1):
        if not pixel_color_is_similar(background_rgb, input_img_rgb_pixels[current_x, y]):
            left = current_x + 1
            break
        if left is None:
            left = 0
    LOG.debug('Viewport left edge is {0:d}'.format(left))

    # Find the right edge
    for current_x in range(int(math.floor(width / 2)), width):
        if not pixel_color_is_similar(background_rgb, input_img_rgb_pixels[current_x, y]):
            right = current_x - 1
            break
        if right is None:
            right = width
    LOG.debug('Viewport right edge is {0:d}'.format(right))

    # Find the top edge
    for current_y in range(int(math.floor(height / 2)), -1, -1):
        if not pixel_color_is_similar(background_rgb, input_img_rgb_pixels[x, current_y]):
            top = current_y + 1
            break
        if top is None:
            top = 0
    LOG.debug('Viewport top edge is {0:d}'.format(top))

    # Find the bottom edge
    for current_y in range(int(math.floor(height / 2)), height):
        if not pixel_color_is_similar(background_rgb, input_img_rgb_pixels[x, current_y]):
            bottom = current_y - 1
            break
        if bottom is None:
            bottom = height
    LOG.debug('Viewport bottom edge is {0:d}'.format(bottom))

    viewport = {'x': left, 'y': top, 'width': (right - left), 'height': (bottom - top)}

    return viewport
