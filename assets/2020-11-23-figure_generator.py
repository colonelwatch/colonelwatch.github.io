import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter

X_1 = 0.5


x = np.linspace(-2*np.pi, 2*np.pi, 1000)
def f_1(x, alpha):
    return np.sin(x)+alpha*np.sin(2*x)

fig, ax = plt.subplots()

ax.plot(x, f_1(x, 0.2))

ax.set_xlim(-2*np.pi, 2*np.pi)

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Plot of $f_1(x)$ for $\alpha=0.2$')

plt.show()


x = np.linspace(-np.pi, np.pi, 1000)
def f(x):
    return np.sin(x)

fig, ax = plt.subplots()

ax.plot(x, f(x))
ax.plot(x, f_1(x, 0.2))

ax.axhline(X_1, color='grey', linestyle='dashed')
ax.axvline(np.arcsin(X_1), color='grey', linestyle='dashed')
ax.axvline(np.arcsin(-X_1)+np.pi, color='grey', linestyle='dashed')

ax.annotate('x = x_1', (np.arcsin(X_1)+0.05, -0.5))
ax.annotate('x = x_2', (np.arcsin(-X_1)+np.pi+0.05, -0.5))

ax.set_xlim(-np.pi, np.pi)
ax.set_ylim(-1.25, 1.25)

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Plot of $\sin(x)$ and $f_1(x)$ for $\alpha=0.2$')

plt.show()


x = np.linspace(-np.pi, np.pi, 1000)
def f_2(x, alpha):
    return np.sin(x)+alpha*np.sin(2*x-np.pi/2)

fig, ax = plt.subplots()

ax.plot(x, f(x))
ax.plot(x, f_2(x, 0.2))

ax.axhline(X_1, color='grey', linestyle='dashed')
ax.axvline(np.arcsin(X_1), color='grey', linestyle='dashed')
ax.axvline(np.arcsin(-X_1)+np.pi, color='grey', linestyle='dashed')

ax.annotate('x = x_1', (np.arcsin(X_1)+0.05, -0.5))
ax.annotate('x = x_2', (np.arcsin(-X_1)+np.pi+0.05, -0.5))

ax.set_xlim(-np.pi, np.pi)
ax.set_ylim(-1.25, 1.25)

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Plot of $\sin(x)$ and $f_2(x)$ for $\alpha=0.2$')

plt.show()


x = np.linspace(-2*np.pi, 2*np.pi, 1000)
def f_3(x, alpha):
    return (np.sin(x)+alpha*np.sin(2*x-np.pi/2)+alpha)/(1+2*alpha)

fig, ax = plt.subplots()

ax.plot(x, f(x))
ax.plot(x, f_3(x, 0.2))

ax.set_xlim(-2*np.pi, 2*np.pi)
ax.set_ylim(-1.25, 1.25)

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Plot of $\sin(x)$ and $f_3(x)$ for $\alpha=0.2$')

plt.show()


x = np.linspace(-1, 1, 1000)

fig, ax = plt.subplots()

ax.plot(x, x)
ax.plot(x, f_3(np.arcsin(x), 0.2))

ax.legend(['normal', 'distortion'])

ax.yaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Distortion LUT plot generated from $f_3(x)$ for $\alpha=0.2$')
plt.xlabel('LUT input', labelpad=120)
plt.ylabel('LUT output', labelpad=110)

axes=plt.gca()
axes.set_aspect('equal')
plt.show()