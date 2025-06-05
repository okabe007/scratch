import numpy as np
import matplotlib.pyplot as plt

def draw_medium(ax, constants):
    shape = constants["shape"]
    if shape == "drop":
        r = constants["drop_r"]
        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        x = r * np.cos(u) * np.sin(v)
        y = r * np.sin(u) * np.sin(v)
        z = r * np.cos(v)
        ax.plot_surface(x, y, z, color='pink', alpha=0.2)
    # 他の shape（cube, spotなど）を描画したい場合はここに追記

def draw_egg_3d(ax, egg_center, radius):
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = radius * np.cos(u) * np.sin(v) + egg_center[0]
    y = radius * np.sin(u) * np.sin(v) + egg_center[1]
    z = radius * np.cos(v) + egg_center[2]
    ax.plot_surface(x, y, z, color='gold', alpha=0.8)
