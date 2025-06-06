import os
import sys

# プロジェクトルート（trajectory_reboot）を取得
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# パスに追加（重複追加を防ぐ）
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tkinter import Tk
from spermsim.initialization import SimApp, load_config
from core.simulation_core import SpermSimulation  # ←← これに変更

REQUIRED_KEYS = [
    "drop_r", "step_length", "number_of_sperm",
    "x_min", "x_max", "y_min", "y_max", "z_min", "z_max",
    "egg_center", "limit"
]

def check_config_validity(constants: dict):
    missing = [k for k in REQUIRED_KEYS if k not in constants]
    if missing:
        raise ValueError(
            f"[ERROR] sperm_config.ini に以下の派生変数が含まれていません:\n{missing}\n"
            "→ GUIで保存（[保存して終了] ボタン）を完了してください。"
        )

def main():
    # 1. GUI 起動
    print("[ENTRY] GUIを起動します...")
    root = Tk()
    app = SimApp(root)
    root.mainloop()  # GUIが閉じられるまで待機

    # 2. .ini 読み込み
    config_path = "sperm_config.ini"
    if not os.path.exists(config_path):
        raise FileNotFoundError("[ERROR] sperm_config.ini が見つかりません。保存して終了を押しましたか？")

    constants = load_config()
    check_config_validity(constants)

    # 3. シミュレーション実行
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)

    sim = SpermSimulation()
    sim.run(constants, result_dir, "simulation_result", save_flag=True)

    print("[ENTRY] シミュレーション完了。")

if __name__ == "__main__":
    main()
