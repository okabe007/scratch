from simcore.motion_modes.cube_mode import CubeMode
from simcore.motion_modes.drop_mode import DropMode
from simcore.motion_modes.spot_mode import SpotMode
from simcore.motion_modes.reflection_mode import ReflectionMode
from tools.enums import IOStatus


import numpy as np
from tools.derived_constants import calculate_derived_constants

class SimulationEngine:
    def __init__(self, constants: dict):
        print("[DEBUG] SimulationEngine.__init__ が呼び出されました")
        self.constants = calculate_derived_constants(constants)
        self.shape = self.constants.get("shape", "cube").lower()
        self.number_of_sperm = self.constants.get("number_of_sperm", 10)
        self.number_of_steps = int(self.constants.get("sim_min", 1.0) * self.constants.get("sample_rate_hz", 4.0) * 60)
        self.step_length = self.constants.get("step_length", 0.01)
        self.seed = int(self.constants.get("seed_number", 0))
        self.rng = np.random.default_rng(self.seed)
        self.motion_mode = self._select_mode()
        print(f"[DEBUG] 選択されたモード: {self.shape}")

    def _select_mode(self):
        if self.shape == "cube":
            return CubeMode(self.constants)
        elif self.shape == "drop":
            return DropMode(self.constants)
        elif self.shape == "spot":
            return SpotMode(self.constants)
        elif self.shape == "reflection":
            return ReflectionMode(self.constants)
        else:
            raise ValueError(f"[ERROR] Unknown shape mode: {self.shape}")

    
    def simulate(self, on_progress=None):
        initial_position = self.constants['initial_position']
        trajectories = np.full((self.number_of_sperm, self.number_of_steps, 3), np.nan)
        vectors = np.zeros((self.number_of_sperm, self.number_of_steps, 3))

        for j in range(self.number_of_sperm):
            position = self._generate_initial_position()
            vector = np.array([0, 0, 1])  # 初期方向を適切に設定
            stick_status = 0  # 初期吸着状態

            for i in range(self.number_of_steps):
                position, vector, stick_status, status = self.motion_mode.drop_polygon_move(
                    position, vector, stick_status, self.constants
                )

                # 常に軌跡を記録する（警告があってもデータは保存される）
                trajectories[j, i] = position
                vectors[j, i] = vector

                if status not in [IOStatus.ON_POLYGON, IOStatus.INSIDE]:
                    print(f"[WARNING]engine.py内部の警告 Unexpected status: {status}")

            if on_progress:
                on_progress(j, self.number_of_sperm)
        
        print("[確認用] 軌跡データ:", trajectories[0, :10, :])  # 軌跡確認用
        return trajectories, vectors

    
    # def simulate(self, on_progress=None):
    #     initial_position = self.constants['initial_position']
    #     print(f"確認：初期位置 = {initial_position}")
    #     print("[DEBUG] engine.py/simulate() 開始")
    #     trajectories = np.full((self.number_of_sperm, self.number_of_steps, 3), np.nan)
    #     vectors = np.zeros((self.number_of_sperm, self.number_of_steps, 3))

    #     for j in range(self.number_of_sperm):
    #         print(f"[DEBUG] engine.py/simulate(): 精子 {j} の初期位置生成")
    #         init_pos = self._generate_initial_position()
    #         print(f"[DEBUG] engine.py/simulate(): 精子 {j} 軌道計算開始")
    #         traj, vecs = self.motion_mode.simulate_trajectory(j, init_pos, self.rng)
    #         print(f"[DEBUG] engine.py/simulate(): 精子 {j} 軌道計算完了")
    #         trajectories[j] = traj
    #         vectors[j] = vecs

    #         if on_progress:
    #             on_progress(j, self.number_of_sperm)

    #     print("[DEBUG] engine.py/simulate() 完了")
    #     return trajectories, vectors

    def _generate_initial_position(self) -> np.ndarray:
        x_len = self.constants.get("medium_x_len", 1.0)
        y_len = self.constants.get("medium_y_len", 1.0)
        z_len = self.constants.get("medium_z_len", 1.0)

        return self.rng.uniform(
            low=[-x_len/2, -y_len/2, -z_len/2],
            high=[x_len/2, y_len/2, z_len/2]
        )
