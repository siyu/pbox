__author__ = 'siy'

import matplotlib.pyplot as plt
import numpy as np
import math as math

t = np.arange(0, 5, 0.2)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
num_series = 2
for i in range(1, num_series + 1):
    label = 'line ' + str(i)
    ax.plot(t, t ** i, '-', label='line ' + str(i))
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('AIG', y=1.1)

box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width, box.height * 0.9])

ax.legend(loc='upper center', ncol=math.ceil(num_series/2), fancybox=True, shadow=True, bbox_to_anchor=(0.5, 1.12))

# background vertical lines
plt.gca().yaxis.grid(True)

plt.show()



