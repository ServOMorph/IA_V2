def lighten_color(color, factor=0.15):
    return tuple(min(1.0, c + factor) for c in color[:3]) + (color[3],)
