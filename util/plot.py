__author__ = 'siy'

import matplotlib.pyplot as plt
import math as math

def plot(title, xlabel, ylabel, series):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(title, y=1.1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for s in series:
        ax.plot(s['x'], s['y'], s['marker'], label=s['label'])

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height * 0.9])

    ax.legend(loc='upper center', ncol=math.ceil(len(series)/2), fancybox=True, shadow=True, prop={'size':10}, bbox_to_anchor=(0.5, 1.12))

    # background vertical lines
    plt.gca().yaxis.grid(True)

    plt.show()
