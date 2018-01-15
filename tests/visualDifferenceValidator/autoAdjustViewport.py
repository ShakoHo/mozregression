from windowController import WindowObject


def lock_window_pos(browser_type, exec_config={}, height_adjustment=0, width_adjustment=0):
    window_title_list = get_browser_name_list(browser_type)
    # Moving window by strings from window_title
    window_obj = WindowObject(window_title_list)

    # First launch or just move position only need to get browser size from settings
    if (not height_adjustment and not width_adjustment) or sys.platform == 'linux2':
        if not exec_config:
            height = Environment.DEFAULT_BROWSER_HEIGHT
            width = Environment.DEFAULT_BROWSER_WIDTH
        else:
            height = exec_config['browser-height']
            width = exec_config['browser-width']
    else:
        window_obj.get_window_rect()
        browser_width = window_obj.rect[2]
        browser_height = window_obj.rect[3]
        height = browser_height + height_adjustment
        width = browser_width + width_adjustment
    window_obj.move_window_pos(0, 0, window_height=height, window_width=width)
    return height, width


def adjust_viewport(browser_type, viewport, exec_config):
    height_adjustment = exec_config['viewport-height'] - viewport['height']
    width_adjustment = exec_config['viewport-width'] - viewport['width']
    height, width = lock_window_pos(browser_type, exec_config, height_adjustment, width_adjustment)
    return height, width


def is_expected_viewport(viewport, exec_config):
    if viewport['height'] == exec_config['viewport-height'] and viewport['width'] == exec_config['viewport-width']:
        return True
    else:
        return False


def is_above_half_viewport(viewport, exec_config):
    half_viewport_height = exec_config['viewport-height'] * 0.5
    half_viewport_width = exec_config['viewport-width'] * 0.5
    if viewport['height'] >= half_viewport_height and viewport['width'] >= half_viewport_width:
        return True
    else:
        return False
