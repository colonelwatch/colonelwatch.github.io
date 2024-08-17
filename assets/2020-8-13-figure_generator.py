import numpy as np
from matplotlib import pyplot as plt

c_range = np.linspace(0, 1, 100)[1:] # Avoid division by zero

g_1 = c_range
db_1 = 20*np.log10(g_1)

plt.plot(c_range, db_1)
plt.xlabel('c')
plt.ylabel('dB')
plt.ylim([-30, 0])
plt.grid(True)
plt.title('Loudness of linear-taper')

plt.savefig('images/2020-8-13-figure4.png', dpi=300)
plt.clf()


g_2 = (0.12*c_range)/(0.12+c_range-c_range**2)
db_2 = 20*np.log10(g_2)

plt.plot(c_range, db_2)
plt.xlabel('c')
plt.ylabel('dB')
plt.ylim([-30, 0])
plt.grid(True)
plt.title('Loudness of linear-taper and loading resistor')

plt.savefig('images/2020-8-13-figure9.png', dpi=300)
plt.clf()

z_s = 1000
z_l = 120000
r_1 = 100000
r_2 = 12000
r_upper = z_s + (1-c_range)*r_1
r_lower = 1/(1/(r_1*c_range)+1/r_2+1/z_l)
g_3 = r_lower/(r_upper+r_lower)
db_3 = 20*np.log10(g_3)

plt.plot(c_range, db_3)
plt.plot(c_range, db_2, alpha=0.5, c='gray')
plt.legend(['With neglectable impedances', 'Without impedances'])
plt.xlabel('c')
plt.ylabel('dB')
plt.ylim([-30, 0])
plt.grid(True)
plt.title('Loudness of linear-taper, loading resistor, and impedances')

plt.savefig('images/2020-8-13-figure12.png', dpi=300)
plt.clf()


g_4 = -c_range/(0.12-c_range+1)
db_4 = 20*np.log10(np.abs(g_4))

plt.plot(c_range, db_4)
plt.xlabel('c')
plt.ylabel('dB')
plt.ylim([-30, 20])
plt.grid(True)
plt.title('Loudness of "second-order" pseudo-logarithmic method')

plt.savefig('images/2020-8-13-figure14.png', dpi=300)
plt.clf()