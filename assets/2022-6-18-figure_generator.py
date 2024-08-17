import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter

x = np.linspace(-0.5*np.pi, 0.5*np.pi, 1000)
def T_4(x):
    return 8*(x**4)-8*(x**2)+1

fig, ax = plt.subplots()

ax.plot(x, np.cos(4*x))
ax.plot(x, T_4(x))

ax.set_xlim(-0.5*np.pi, 0.5*np.pi)
ax.set_ylim(-1.25, 1.25)

ax.spines['left'].set_position('zero')
ax.spines['right'].set_color('none')
ax.yaxis.tick_left()
ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.xaxis.tick_bottom()

plt.title(r'Plot of $T_4(x)$ and $\cos(4 x)$')

plt.show()


x = np.linspace(-1, 1, 1000)
def f_3(x, alpha):
    return (np.sin(x)+alpha*np.sin(2*x-np.pi/2)+alpha)/(1+2*alpha)
def f_2(x):
    return (2/7)*x**2+(5/7)*x

fig, [ax1, ax2] = plt.subplots(1, 2)

ax1.plot(x, x)
ax1.plot(x, f_3(np.arcsin(x), 0.2))
ax1.legend(['normal', 'distortion'])
ax1.yaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
ax1.spines['left'].set_position('zero')
ax1.spines['right'].set_color('none')
ax1.yaxis.tick_left()
ax1.spines['bottom'].set_position('zero')
ax1.spines['top'].set_color('none')
ax1.xaxis.tick_bottom()
ax1.set_title(r'Old waveshaper function for $\alpha=0.2$')
ax1.set_xlabel('LUT input', labelpad=120)
ax1.set_ylabel('LUT output', labelpad=110)

ax2.plot(x, x)
ax2.plot(x, f_2(x), 0.2)
ax2.legend(['normal', 'distortion'])
ax2.yaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
ax2.spines['left'].set_position('zero')
ax2.spines['right'].set_color('none')
ax2.yaxis.tick_left()
ax2.spines['bottom'].set_position('zero')
ax2.spines['top'].set_color('none')
ax2.xaxis.tick_bottom()
ax2.set_title(r'New waveshaper function for $\alpha=0.2$')
ax2.set_xlabel('LUT input', labelpad=120)
ax2.set_ylabel('LUT output', labelpad=110)

axes=plt.gca()
axes.set_aspect('equal')
plt.show()