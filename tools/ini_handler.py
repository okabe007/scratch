import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "sperm_config.ini")

PARAM_ORDER = [
    "shape", "spot_angle", "vol", "sperm_conc", "vsl", "deviation",
    "surface_time", "egg_localization", "gamete_r", "sim_min",
    "sample_rate_hz", "seed_number", "sim_repeat", "display_mode",
]

default_values = {
    "shape": "cube",
    "spot_angle": 50.0,
    "vol": 6.25,
    "sperm_conc": 10_000.0,
    "vsl": 0.13,
    "deviation": 0.4,
    "surface_time": 2.0,
    "egg_localization": "bottom_center",
    "gamete_r": 0.04,
    "sim_min": 1.0,
    "sample_rate_hz": 4.0,
    "seed_number": "None",
    "sim_repeat": 1,
    "display_mode": ["2D"],
}

def save_config(values: dict) -> None:
    cfg = configparser.ConfigParser()
    ordered = {}
    for k in PARAM_ORDER:
        if k in values:
            v = values[k]
            ordered[k] = ",".join(v) if isinstance(v, list) else str(v)
    for k in sorted(values.keys()):
        if k not in ordered:
            ordered[k] = str(values[k])
    cfg["simulation"] = ordered
    with open(CONFIG_PATH, "w") as f:
        cfg.write(f)

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        save_config(default_values)
        return default_values.copy()

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH)
    values = default_values.copy()
    c = cfg["simulation"]

    for k in PARAM_ORDER:
        raw = c.get(k, str(default_values[k]))
        try:
            if k in ["vsl", "spot_angle", "gamete_r", "sperm_conc", "vol", "sample_rate_hz", "sim_min"]:
                values[k] = float(raw)
            elif k == "sim_repeat":
                values[k] = int(float(raw))
            elif k == "display_mode":
                values[k] = [v for v in raw.split(",") if v]
            else:
                values[k] = raw
        except Exception:
            values[k] = raw
    return values
