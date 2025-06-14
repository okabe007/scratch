import os
import tkinter as tk
from tkinter import ttk
import configparser
import numpy as np
import math
from core.simulation_core import SpermSimulation
from tools.plot_utils import plot_2d_trajectories # plot_3d_trajectories
from tools.derived_constants import calculate_derived_constants
import sys
# from tools.movie_utils import render_3d_movie
import sys
from pathlib import Path
# プロジェクトのルートパスを追加
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))
# プロジェクトのルートパスを取得（このファイルの親フォルダ）
project_root = os.path.abspath(os.path.dirname(__file__))
# ルートがsys.pathに含まれていなければ追加
if project_root not in sys.path:
    sys.path.insert(0, project_root)
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sperm_config.ini")
# 保存時のキー順（GUI 表示順と合わせる）
PARAM_ORDER = [
    "shape", "spot_angle", "vol", "sperm_conc", "vsl", "deviation",
    "surface_time", "egg_localization", "gamete_r", "sim_min",
    "sample_rate_hz", "seed_number", "sim_repeat", "display_mode",
]
# デフォルト設定
default_values = {
    "shape": "cube",
    "spot_angle": 50.0,
    "vol": 6.25,               # µL
    "sperm_conc": 10_000.0,    # cells/mL
    "vsl": 0.13,               # mm/s
    "deviation": 0.4,
    "surface_time": 2.0,
    "egg_localization": "bottom_center",
    "gamete_r": 0.04,          # mm  (GUI 表示は µm)
    "sim_min": 1.0,            # min 実測値ではなく「分」→秒に変換は simulation 側
    "sample_rate_hz": 4.0,
    "seed_number": "None",
    "sim_repeat": 1,
    "display_mode": ["2D"],    # 文字列リスト
}
def save_config(values: dict) -> None:
    cfg = configparser.ConfigParser()
    ordered = {}
    for k in PARAM_ORDER:
        if k not in values:
            continue
        v = values[k]
        if k == "display_mode":
            ordered[k] = ",".join(v) if isinstance(v, list) else str(v)
        else:
            ordered[k] = str(v)
    # 保存対象外のキーもまとめて保存
    for k in sorted(values.keys()):
        if k in ordered or k in PARAM_ORDER:
            continue
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

    # 型を安全に解釈
    for k in PARAM_ORDER:
        raw = c.get(k, str(default_values[k]))
        try:
            if k in ["vsl", "spot_angle", "gamete_r", "sperm_conc",
                     "vol", "sample_rate_hz", "sim_min"]:
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
# ---------------------------------------------------------------------------
# Tkinter GUI クラス
# ---------------------------------------------------------------------------
class SimApp(tk.Tk):
    def __init__(self) -> None:
        
        super().__init__()
        self.title("Sperm Simulation GUI")
        self.geometry("780x900")
        self.config_data = load_config()  # .ini → dict
        self.tk_vars: dict[str, tk.Variable] = {}  # Param ↔ Tk 変数
        self.save_var = tk.BooleanVar()
        self.save_var.set(True)
        # スクロールキャンバス
        canvas = tk.Canvas(self)
        vbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        self.scroll_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vbar.set)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")

        # 各ウィジェットを配置
        self._create_widgets(self.scroll_frame)
        self._restore_from_config()  # 値を復元
        ttk.Checkbutton
    # ---------------------------------------------------------------------
    # ウィジェット生成
    # ---------------------------------------------------------------------
    def _create_widgets(self, parent: ttk.Frame) -> None:
        # --- shape -------------------------------------------------------
        self.tk_vars["shape"] = tk.StringVar()
        ttk.Label(parent, text="shape:").pack(anchor="w", padx=10, pady=(10, 0))
        f_shape = ttk.Frame(parent); f_shape.pack(anchor="w", padx=30)
        for v in ["cube", "drop", "spot", "ceros"]:
            ttk.Radiobutton(f_shape, text=v, variable=self.tk_vars["shape"],
                            value=v, command=self._update_spot_angle_state
                            ).pack(side="left")

        # --- spot_angle --------------------------------------------------
        self.tk_vars["spot_angle"] = tk.DoubleVar()
        ttk.Label(parent, text="spot_angle (deg):").pack(anchor="w", padx=10, pady=(10, 0))
        f_angle = ttk.Frame(parent); f_angle.pack(anchor="w", padx=30)
        self.spot_angle_buttons = []
        for v in [30, 50, 70, 90]:
            rb = ttk.Radiobutton(f_angle, text=str(v),
                                 variable=self.tk_vars["spot_angle"], value=float(v))
            rb.pack(side="left")
            self.spot_angle_buttons.append(rb)

        # --- vol ---------------------------------------------------------
        self.tk_vars["vol"] = tk.DoubleVar()
        ttk.Label(parent, text="vol (µL):").pack(anchor="w", padx=10, pady=(10, 0))
        f_vol = ttk.Frame(parent); f_vol.pack(anchor="w", padx=30)
        for v in [6.25, 12.5, 25, 50, 100, 200]:
            ttk.Radiobutton(f_vol, text=str(v), variable=self.tk_vars["vol"],
                            value=float(v)).pack(side="left")

        # --- sperm_conc --------------------------------------------------
        self.tk_vars["sperm_conc"] = tk.DoubleVar()
        ttk.Label(parent, text="sperm_conc (cells/mL):").pack(anchor="w", padx=10, pady=(10, 0))
        f_conc = ttk.Frame(parent); f_conc.pack(anchor="w", padx=30)
        for v in [1e3, 3.16e3, 1e4, 3.162e4, 1e5]:
            ttk.Radiobutton(f_conc, text=f"{int(v):,}", variable=self.tk_vars["sperm_conc"],
                            value=float(v)).pack(side="left")

        # --- vsl ---------------------------------------------------------
        self.tk_vars["vsl"] = tk.DoubleVar()
        ttk.Label(parent, text="vsl (µm/s):").pack(anchor="w", padx=10, pady=(10, 0))
        f_vsl = ttk.Frame(parent); f_vsl.pack(anchor="w", padx=30)
        for v in [73, 90, 110, 130, 150]:
            ttk.Radiobutton(f_vsl, text=str(v), variable=self.tk_vars["vsl"],
                            value=float(v)).pack(side="left")

        # --- deviation ---------------------------------------------------
        self.tk_vars["deviation"] = tk.DoubleVar()
        ttk.Label(parent, text="deviation:").pack(anchor="w", padx=10, pady=(10, 0))
        f_dev = ttk.Frame(parent); f_dev.pack(anchor="w", padx=30)
        for v in [0.1, 0.2, 0.4, 0.8, 1.0, 2.0, 4.0]:
            ttk.Radiobutton(f_dev, text=str(v), variable=self.tk_vars["deviation"],
                            value=float(v)).pack(side="left")

        # --- surface_time ------------------------------------------------
        self.tk_vars["surface_time"] = tk.DoubleVar()
        ttk.Label(parent, text="surface_time (sec):").pack(anchor="w", padx=10, pady=(10, 0))
        f_surface = ttk.Frame(parent); f_surface.pack(anchor="w", padx=30)
        for v in [0, 1, 2, 3, 4]:
            ttk.Radiobutton(f_surface, text=str(v), variable=self.tk_vars["surface_time"],
                            value=float(v)).pack(side="left")

        # --- egg_localization -------------------------------------------
        self.tk_vars["egg_localization"] = tk.StringVar()
        ttk.Label(parent, text="egg_localization:").pack(anchor="w", padx=10, pady=(10, 0))
        f_egg = ttk.Frame(parent); f_egg.pack(anchor="w", padx=30)
        for v in ["bottom_center", "bottom_edge", "center"]:
            ttk.Radiobutton(f_egg, text=v, variable=self.tk_vars["egg_localization"],
                            value=v).pack(side="left")

        # --- gamete_r ----------------------------------------------------
        self.tk_vars["gamete_r"] = tk.DoubleVar()
        ttk.Label(parent, text="gamete_r (µm):").pack(anchor="w", padx=10, pady=(10, 0))
        f_gr = ttk.Frame(parent); f_gr.pack(anchor="w", padx=30)
        for v in [40, 50, 150]:
            ttk.Radiobutton(f_gr, text=str(v), variable=self.tk_vars["gamete_r"],
                            value=float(v)).pack(side="left")

        # --- sim_min -----------------------------------------------------
        self.tk_vars["sim_min"] = tk.DoubleVar()
        ttk.Label(parent, text="sim_min (min):").pack(anchor="w", padx=10, pady=(10, 0))
        f_simmin = ttk.Frame(parent); f_simmin.pack(anchor="w", padx=30)
        for v in [0.2, 1, 10, 30, 60]:
            ttk.Radiobutton(f_simmin, text=str(v), variable=self.tk_vars["sim_min"],
                            value=float(v)).pack(side="left")

        # --- sample_rate_hz ----------------------------------------------
        self.tk_vars["sample_rate_hz"] = tk.DoubleVar()
        ttk.Label(parent, text="sample_rate_hz:").pack(anchor="w", padx=10, pady=(10, 0))
        f_hz = ttk.Frame(parent); f_hz.pack(anchor="w", padx=30)
        for v in [1, 2, 3, 4]:
            ttk.Radiobutton(f_hz, text=str(v), variable=self.tk_vars["sample_rate_hz"],
                            value=float(v)).pack(side="left")

        # --- seed_number ----------------------------------------------
        self.tk_vars["seed_number"] = tk.StringVar()
        ttk.Label(parent, text="seed_number:").pack(anchor="w", padx=10, pady=(10, 0))
        f_seed = ttk.Frame(parent); f_seed.pack(anchor="w", padx=30)
        for v in ["None", "0", "1", "2", "3", "4"]:
            ttk.Radiobutton(f_seed, text=v, variable=self.tk_vars["seed_number"],
                            value=v).pack(side="left")

        # --- sim_repeat --------------------------------------------------
        self.tk_vars["sim_repeat"] = tk.IntVar()
        ttk.Label(parent, text="sim_repeat:").pack(anchor="w", padx=10, pady=(10, 0))
        f_repeat = ttk.Frame(parent); f_repeat.pack(anchor="w", padx=30)
        for v in [1, 3, 10, 30]:
            ttk.Radiobutton(f_repeat, text=str(v), variable=self.tk_vars["sim_repeat"],
                            value=int(v)).pack(side="left")

        # --- display_mode ラジオボタン ------------------------------
        # ini ファイルからの正しい読み込み方法
        display_mode = self.config_data.get('display_mode', '2D')

        # 万が一、タプルになっている場合を考えて厳密に処理
        if isinstance(display_mode, tuple):
            display_mode = display_mode[0]
        elif isinstance(display_mode, list):
            display_mode = display_mode[0]

        # 念のために文字列変換と空白削除
        display_mode = str(display_mode).strip().replace('(', '').replace(')', '').replace(',', '').replace("'", "").replace('"', '')

        self.tk_vars["display_mode"] = tk.StringVar(value=display_mode)

        ttk.Label(parent, text="display_mode:").pack(anchor="w", padx=10, pady=(10, 0))
        f_disp = ttk.Frame(parent)
        f_disp.pack(anchor="w", padx=30)

        for v in ["2D", "3D", "movie"]:
            ttk.Radiobutton(
                f_disp, text=v, variable=self.tk_vars["display_mode"], value=v
            ).pack(side="left")

        # 最終確認のプリント文
        print(f"最終修正後の表示モード: {self.tk_vars['display_mode'].get()}")

        # --- 実行ボタン --------------------------------------------------
        ttk.Button(parent, text="Save settings and run simulation",
                   command=self._on_save).pack(pady=20)

        self._update_spot_angle_state()
    # ---------------------------------------------------------------------
    # spot_angle の有効／無効
    # ---------------------------------------------------------------------
    def _update_spot_angle_state(self) -> None:
        enable = (self.tk_vars["shape"].get() == "spot")
        state = "normal" if enable else "disabled"
        for rb in self.spot_angle_buttons:
            rb.config(state=state)
    # ---------------------------------------------------------------------
    # 保存＆シミュレーション実行
    # ---------------------------------------------------------------------
        # ---------------------------------------------------------------------
    # 保存＆シミュレーション実行  ← ★ここを全面差し替え★
    # ---------------------------------------------------------------------
    def _on_save(self):
        # GUI入力から定数を取得し、派生変数を計算
        constants = {key: var.get() for key, var in self.tk_vars.items()}
        constants = calculate_derived_constants(constants)

        print("[デバッグ追加] 派生変数計算後のconstants:", constants)

        # シミュレーションの初期化と実行
        sim = SpermSimulation(constants)

        result_dir = "results"
        save_name = "simulation_result"
        save_flag = self.save_var.get()

        sim.run(constants, result_dir, save_name, save_flag)

        # 表示モードに応じて描画処理を分岐
        display_mode = self.tk_vars["display_mode"].get().strip()
        print(f"[確認] 描画モード：{display_mode}")

        if display_mode == '2D':
            from tools.plot_utils import plot_2d_trajectories
            plot_2d_trajectories(sim.trajectory, sim.constants)

        elif display_mode == '3D':
            from tools.plot_utils import plot_3d_movie_trajectories
            plot_3d_movie_trajectories(sim.trajectory, sim.constants)
        elif display_mode == 'movie':
            from spermsim.coremovie import render_3d_movie
            # render_3d_movie(sim.trajectory, sim.vectors, sim.constants)
            render_3d_movie(
                sim.trajectory,
                sim.vectors,
                sim.constants,
                save_path="movie.mp4",
                show=False
            )

        else:
            raise ValueError(f"無効な描画モードです: {display_mode}")

        # 設定を保存
        save_config(constants)

    # ---------------------------------------------------------------------
    # 起動時に .ini から各 Tk 変数を復元
    # ---------------------------------------------------------------------
    def _restore_from_config(self) -> None:
        for k, var in self.tk_vars.items():
            if k not in self.config_data:
                continue
            v = self.config_data[k]
            try:
                if isinstance(var, tk.DoubleVar):
                    val = float(v)
                    if k == "vsl":
                        val *= 1000.0  # mm/s → µm/s
                    elif k == "gamete_r":
                        val *= 1000.0  # mm  → µm
                    var.set(val)
                elif isinstance(var, tk.IntVar):
                    var.set(int(float(v)))
                else:
                    var.set(str(v))
            except Exception:
                var.set(v)
        # display_mode
        modes = self.config_data.get("display_mode", [])
        if isinstance(modes, list) and modes:
            self.tk_vars["display_mode"].set(modes[0])
        elif isinstance(modes, str):
            self.tk_vars["display_mode"].set(modes)
# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("[DEBUG] starting SimApp ...")
    app = SimApp()
    app.mainloop()