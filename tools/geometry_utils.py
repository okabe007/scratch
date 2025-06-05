# tools/geometry_utils.py

import math

def calc_spot_geometry(vol_mm3: float, angle_deg: float):
    """
    spot（球冠）形状の体積と角度から、球の半径、底面半径、底面高さを返す。
    """
    theta = math.radians(angle_deg)
    h = (3 * vol_mm3 / (math.pi * (1 - math.cos(theta)) ** 2 * (2 + math.cos(theta)))) ** (1/3)
    R = h / (1 - math.cos(theta))
    r = R * math.sin(theta)
    return R, r, h
