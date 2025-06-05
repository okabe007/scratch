import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tools.visual_utils import draw_medium, draw_egg_3d  # 必要に応じて調整

def render_3d_movie(
    trajs: np.ndarray,
    vectors: np.ndarray,
    constants: dict,
    save_path=None,
    show=True
):
    print('[DEBUG] render_3d_movie 呼ばれた shape:', constants.get('shape'))
    all_norms = np.linalg.norm(vectors.reshape(-1, 3), axis=1)
    print(f"[DEBUG] vectors 長さの範囲: min={all_norms.min():.4g}, max={all_norms.max():.4g}")

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 軸設定
    xlim = constants["x_min"], constants["x_max"]
    ylim = constants["y_min"], constants["y_max"]
    zlim = constants["z_min"], constants["z_max"]
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_box_aspect([
        xlim[1] - xlim[0],
        ylim[1] - ylim[0],
        zlim[1] - zlim[0]
    ])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Sperm Vectors (Fixed Length)")

    # 卵子とメディウムの初期描画
    draw_medium(ax, constants)
    egg_pos = constants["egg_center"]
    egg_radius = constants.get("gamete_r", 0.05)
    draw_egg_3d(ax, egg_pos, egg_radius)

    # データ準備
    num_sperm = trajs.shape[0]
    num_frames = trajs.shape[1]

    # 色（赤抜き19色）
    full_colors = plt.cm.tab20(np.linspace(0, 1, 20))
    red_index = 3
    colors = [full_colors[i] for i in range(20) if i != red_index]

    # update関数（毎フレーム描画更新）
    def update(frame):
        ax.cla()

        # 軸とラベル
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_zlim(*zlim)
        ax.set_box_aspect([
            xlim[1] - xlim[0],
            ylim[1] - ylim[0],
            zlim[1] - zlim[0]
        ])
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(f"Frame {frame + 1} / {num_frames}")

        # 卵子・メディウム再描画
        draw_medium(ax, constants)
        draw_egg_3d(ax, egg_pos, egg_radius)

        # 全精子のベクトル描画
        for i in range(num_sperm):
            x, y, z = trajs[i, frame]
            u, v, w = vectors[i, frame]
            norm = np.linalg.norm([u, v, w]) + 1e-12
        
            u, v, w = u / norm, v / norm, w / norm  # ✅ 向きのみ保持（単位ベクトル）

            ax.quiver(
                x, y, z, u, v, w,
                length=0.1,               # ✅ Masaru仕様：表示長さを0.1mmに固定
                normalize=True,           # ✅ 方向ベクトルを正規化
                arrow_length_ratio=0.7,
                linewidth=2,
                color=colors[i % 19]
            )

    # アニメーション生成
    ani = FuncAnimation(
        fig, update,
        frames=num_frames,
        interval=100,
        blit=False
    )

    # 保存 or 表示
    if save_path:
        ani.save(save_path, writer='ffmpeg', fps=10)
    elif show:
        plt.show()

    return ani  # ✅ GC破棄防止
