import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def render_debug_movie():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_title("Test Rotation")

    def update(frame):
        ax.cla()
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_title(f"Frame {frame}")

        angle = 2 * np.pi * frame / 60
        u, v, w = np.cos(angle), np.sin(angle), 0
        ax.quiver(0, 0, 0, u, v, w, length=0.5, normalize=True, color='blue')

    ani = FuncAnimation(fig, update, frames=60, interval=100, blit=False)
    ani.save("debug_movie.mp4", writer='ffmpeg', fps=10)
    print("[INFO] debug_movie.mp4 を保存しました")

if __name__ == "__main__":
    render_debug_movie()
