import numpy as np
import math

def calculate_derived_constants(raw_constants):
    """
    GUIから渡されるraw_constantsに基づき、以下の派生変数を計算して返す：

    - drop_r                  : vol から球の半径を逆算（mm）
    - spot_r, spot_bottom_r,
      spot_bottom_height     : vol + angle_deg から球冠ジオメトリを逆算（mm）
    - edge                   : vol の立方根（cube形状の一辺、mm）
    - step_length            : vsl × sample_rate / 1000（mm/step）
    - egg_center             : gamete_x/y/z_um → mm に変換
    - x_min ～ z_max         : shape に応じた描画範囲（mm）
    """
    constants = raw_constants.copy()
    shape = constants.get("shape", "cube").lower()
    constants["shape"] = shape
    vol = float(constants.get("vol", 0.0))  # μL = mm³

    # 卵子半径 μm → mm
    gamete_r_um = float(constants.get("gamete_r", 50.0))
    gamete_r_mm = gamete_r_um / 1000.0
    constants["gamete_r"] = gamete_r_mm

    # drop_r の自動計算（球体と仮定）
    if shape == "drop" and "drop_r" not in raw_constants:
        r_mm = ((3.0 * vol) / (4.0 * math.pi)) ** (1.0 / 3.0)
        constants["drop_r"] = r_mm

    # spot_r 等の逆算（球冠）
    if shape == "spot" and "spot_r" not in raw_constants:
        angle_deg = float(constants.get("spot_angle", 0.0))
        spot_r_mm, bottom_r_mm, bottom_h_mm = calc_spot_geometry(vol, angle_deg)
        constants["spot_r"] = spot_r_mm
        constants["spot_bottom_r"] = bottom_r_mm
        constants["spot_bottom_height"] = bottom_h_mm

    # edge の計算（cube）
    if shape == "cube":
        edge = vol ** (1.0 / 3.0)
        constants["edge"] = edge

    # step_length = vsl * rate / 1000
    vsl_um_s = float(constants.get("vsl", 0.0))
    sample_rate_hz = float(constants.get("sample_rate_hz", 0.0))
    step_length_mm = (vsl_um_s * sample_rate_hz) / 1000.0
    constants["step_length"] = step_length_mm

    # x/y/z 軸範囲設定
    if shape == "cube":
        half = constants["edge"] / 2
        constants.update(
            x_min=-half, x_max=half,
            y_min=-half, y_max=half,
            z_min=0.0,   z_max=constants["edge"]
        )
    elif shape == "drop":
        r = constants["drop_r"]
        constants.update(
            x_min=-r, x_max=r,
            y_min=-r, y_max=r,
            z_min=0.0, z_max=2 * r
        )
    elif shape == "spot":
        R = constants["spot_r"]
        b_r = constants["spot_bottom_r"]
        constants.update(
            x_min=-b_r, x_max=b_r,
            y_min=-b_r, y_max=b_r,
            z_min=0.0,  z_max=R
        )
    else:
        # fallback: cube相当で囲む
        fallback = vol ** (1.0 / 3.0)
        half = fallback / 2
        constants.update(
            x_min=-half, x_max=half,
            y_min=-half, y_max=half,
            z_min=0.0,   z_max=fallback
        )

    # 卵子中心座標を mm に変換
    egg_x_mm = float(constants.get("gamete_x_um", 0.0)) / 1000.0
    egg_y_mm = float(constants.get("gamete_y_um", 0.0)) / 1000.0
    raw_z_min_um = float(constants.get("spot_bottom_height", 0.0)) * 1000.0 if shape == "spot" else 0.0
    egg_z_mm = (raw_z_min_um + gamete_r_um) / 1000.0
    constants["egg_center"] = np.array([egg_x_mm, egg_y_mm, egg_z_mm])

    return constants

def calc_spot_geometry(volume_ul: float, angle_deg: float) -> tuple[float, float, float]:
    """Return (spot_r_mm, bottom_r_mm, bottom_height_mm) from volume and angle."""
    angle_rad = math.radians(angle_deg)
    vol_um3 = volume_ul * 1e9

    def cap_volume(R: float) -> float:
        h = R * (1 - math.cos(angle_rad))
        return math.pi * h * h * (3 * R - h) / 3

    low = 0.0
    high = max(vol_um3 ** (1 / 3), 1.0)
    while cap_volume(high) < vol_um3:
        high *= 2.0

    for _ in range(60):
        mid = (low + high) / 2.0
        if cap_volume(mid) < vol_um3:
            low = mid
        else:
            high = mid

    R_um = (low + high) / 2.0
    bottom_r_um = R_um * math.sin(angle_rad)
    bottom_height_um = R_um * math.cos(angle_rad)
    return R_um / 1000.0, bottom_r_um / 1000.0, bottom_height_um / 1000.0