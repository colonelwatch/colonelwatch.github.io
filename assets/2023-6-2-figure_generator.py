import numpy as np
from skimage import color
from matplotlib import pyplot as plt

def plot_lab(lab, center=None, title=None):
    c = color.lab2rgb(lab)
    l = lab[:, 0].flatten()
    a = lab[:, 1].flatten()
    b = lab[:, 2].flatten()

    ax = plt.axes(projection="3d")
    ax.scatter3D(a, b, l, c=c)

    if center is not None:
        ax.scatter3D(center[1], center[2], center[0], marker='x')

    if title:
        plt.title(title)

    return ax

# https://en.wikipedia.org/wiki/Rotation_matrix#General_rotations
def rotation_matrix(yaw, pitch, roll):
    yaw_matrix = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1],
    ])
    pitch_matrix = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)],
    ])
    roll_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)],
    ])

    return yaw_matrix @ pitch_matrix @ roll_matrix

lab_soldark = np.array([
    [15, 20, 45, 50, 60, 65, 92, 97, 60, 50, 50, 50, 50, 55, 60, 60],
    [-12, -12, -7, -7, -6, -5, 0, 0, 10, 50, 65, 65, 15, -10, -35, -20],
    [-12, -12, -7, -7, -3, -2, 10, 10, 65, 55, 45, -5, -45, -45, -5, 65],
], dtype=np.float32).T
t_sol = np.array([55.5, -6.125, -2.875])

ax = plot_lab(lab_soldark, t_sol, title='Solarized Dark in CIELAB space')
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_zlabel('L')
plt.savefig('images/2023-6-2-figure1.png', dpi=300)
plt.clf()

mean = [55.5, -6.125, -2.875]
principal_component = [0.95104299, 0.14562397, 0.27260023]
line_pts = np.outer(np.linspace(-42, 42, 10), principal_component)+mean

ax = plot_lab(lab_soldark, t_sol, title='Solarized Dark in CIELAB space')
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_zlabel('L')
plt.plot(line_pts[:, 1], line_pts[:, 2], line_pts[:, 0])
plt.savefig('images/2023-6-2-figure3.png', dpi=300)