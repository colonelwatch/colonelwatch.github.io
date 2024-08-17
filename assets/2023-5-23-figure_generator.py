import numpy as np
from scipy.interpolate import make_smoothing_spline

from matplotlib import animation
from matplotlib import pyplot as plt

EXAMPLE_1_PATH = 'assets/example_1.npy'
EXAMPLE_2_PATH = 'assets/example_2.npy'


class Interpolator:
    def __init__(self, memory_size=512, lam=1e-3):
        self.memory = np.zeros((memory_size, 2))
        self.lam = lam

    def update(self, samples):
        self.memory = np.roll(self.memory, -len(samples), axis=0)
        self.memory[-len(samples):] = samples
    def take(self, x):

        # get samples in ascending order of angle
        angles = self.memory[:, 0]
        argsort_angles = np.argsort(angles)
        angles = angles[argsort_angles]
        distances = self.memory[:, 1][argsort_angles]

        # remove duplicate angles
        angles_dedup = [angles[0]]
        distances_dedup = [distances[0]]
        for i in range(1, len(angles)):
            if angles[i-1] != angles[i]:
                angles_dedup.append(angles[i])
                distances_dedup.append(distances[i])

        # the above was because make_smoothing_spline requires angle[i] > angle[i-1]
        interp_func = make_smoothing_spline(angles_dedup, distances_dedup, lam=self.lam)
        return interp_func(x)

class MaFilter:
    def __init__(self, n_channels=360, n_samples=4):
        self.samples = np.zeros((n_channels, n_samples))
        self.i = 0
    
    def filter(self, x_t):
        self.samples[:, self.i] = x_t
        self.i = (self.i+1)%self.samples.shape[1]
        return np.mean(self.samples, axis=1)

class VelocityEstimator:
    def __init__(self, window_size=16):
        self.h_prev = np.zeros(360)
        self.window_size = window_size

    def estimate(self, h, dt):
        dtheta = 2*np.pi/360
        
        dh_dt = (h-self.h_prev)/dt
        dh_dtheta = (np.roll(h, -1)-np.roll(h, 1))/(2*dtheta)

        dh_dtheta_neighbors = np.empty((360, 2*self.window_size+1), dtype=np.float32)
        dh_dt_neighbors = np.empty((360, 2*self.window_size+1), dtype=np.float32)
        for j in range(2*self.window_size+1):
            shift = j-self.window_size
            dh_dtheta_neighbors[:, j] = np.roll(dh_dtheta, shift)
            dh_dt_neighbors[:, j] = np.roll(dh_dt, shift)
        
        # calculates all estimated velocities as many dot products
        elementwise_product = np.multiply(dh_dtheta_neighbors, dh_dt_neighbors)
        v_est = -np.sum(elementwise_product, axis=1)/np.sum(dh_dtheta_neighbors**2, axis=1)
        
        self.h_prev = h
        return v_est


GRID = np.linspace(0, 2*np.pi, 360)

def generate(path):
    interpolator = Interpolator(512)
    filter = MaFilter(360, 4)
    direct_estimator = VelocityEstimator(0)
    lk_estimator = VelocityEstimator(16)

    samples_batches = np.load(path, allow_pickle=True)
    samples_batches = samples_batches[:, 0]
    samples_batches = [samples[:, (1, 2)] for samples in samples_batches]
    for i in range(len(samples_batches)):
        samples_batches[i][:, 0] *= np.pi/180
        samples_batches[i][:, 1] /= 1000

    grid = np.linspace(0, 2*np.pi, 360)
    interpolations = []
    for samples in samples_batches:
        interpolator.update(samples)
        interpolation = interpolator.take(grid)
        interpolations.append(interpolation)

    filtered_interpolations = []
    for interpolation in interpolations:
        filtered_interpolations.append(filter.filter(interpolation))

    direct_velocities = []
    for interpolation in filtered_interpolations:
        direct_velocities.append(direct_estimator.estimate(interpolation, 1/7))

    lk_velocities = []
    for interpolation in filtered_interpolations:
        lk_velocities.append(lk_estimator.estimate(interpolation, 1/7))
    
    return samples_batches, interpolations, filtered_interpolations, direct_velocities, lk_velocities


# 1) example 1, raw samples + interpolations + filtered interpolations + lk velocity estimation
print('Generating example 1...', end='', flush=True)

samples_batches, interpolations, filtered_interpolations, direct_velocities, lk_velocities = generate(EXAMPLE_1_PATH)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
    ax.plot([], [], color='tab:green', linestyle='-')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    artists[1].set_data(GRID, 10*np.abs(lk_velocities[i]))
    return artists

interval_ms = 100
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure1.gif', writer='pillow')
plt.cla()

print('Done')
    

samples_batches, interpolations, filtered_interpolations, direct_velocities, lk_velocities = generate(EXAMPLE_2_PATH)


# 2) example 2, raw samples
print('Generating samples animation...', end='', flush=True)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    return artists

interval_ms = 100 # actually recorded at 7Hz, but we speed it up a bit to keep consistent with fig 1
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure2.gif', writer='pillow')
plt.cla()

print('Done')


# 3) example 2, raw samples + interpolations
print('Generating samples + interp animation...', end='', flush=True)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
    ax.plot([], [], color='tab:blue', linestyle='-')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    artists[1].set_data(GRID, interpolations[i])
    return artists

interval_ms = 100
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure5.gif', writer='pillow')
plt.cla()

print('Done')


# 4) example 2, raw samples + interpolations + filtered interpolations
print('Generating samples + interp + filt interp animation...', end='', flush=True)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
    ax.plot([], [], color='tab:blue', linestyle='-')[0],
    ax.plot([], [], color='tab:orange', linestyle='-')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    artists[1].set_data(GRID, interpolations[i])
    artists[2].set_data(GRID, filtered_interpolations[i])
    return artists

interval_ms = 100
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure7.gif', writer='pillow')
plt.cla()

print('Done')


# 5) example 2, raw samples + interpolations + filtered interpolations + direct velocity estimation
print('Generating samples + interp + filt interp + direct vel est animation...', end='', flush=True)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
    ax.plot([], [], color='tab:blue', linestyle='-')[0],
    ax.plot([], [], color='tab:orange', linestyle='-')[0],
    ax.plot([], [], color='tab:green', linestyle='-')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    artists[1].set_data(GRID, interpolations[i])
    artists[2].set_data(GRID, filtered_interpolations[i])
    artists[3].set_data(GRID, 10*np.abs(direct_velocities[i]))
    return artists

interval_ms = 100
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure8.gif', writer='pillow')
plt.cla()

print('Done')


# 6) example 2, raw samples + interpolations + filtered interpolations + lk velocity estimation
print('Generating samples + interp + filt interp + lk vel est animation...', end='', flush=True)

fig = plt.figure()
ax = fig.add_subplot(projection='polar')
ax.set_ylim(0, 7)
ax.set_xlim(0, 2*np.pi)

artists = [
    ax.plot([], [], color='tab:blue', marker='x', linestyle='')[0],
    ax.plot([], [], color='tab:blue', linestyle='-')[0],
    ax.plot([], [], color='tab:orange', linestyle='-')[0],
    ax.plot([], [], color='tab:green', linestyle='-')[0],
]

def animate(i):
    artists[0].set_data(samples_batches[i][:, 0], samples_batches[i][:, 1])
    artists[1].set_data(GRID, interpolations[i])
    artists[2].set_data(GRID, filtered_interpolations[i])
    artists[3].set_data(GRID, 10*np.abs(lk_velocities[i]))
    return artists

interval_ms = 100
anim = animation.FuncAnimation(fig, animate, frames=len(samples_batches), interval=interval_ms, blit=True)
anim.save('images/2023-5-26-figure9.gif', writer='pillow')
plt.cla()

print('Done')