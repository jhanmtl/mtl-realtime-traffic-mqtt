import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import backend_utils

minval = 7.5
maxval = 27.5
wl = np.pi / 15

shift = minval
amplitude = maxval - minval


tp=backend_utils.TwoPeaks()
tp.set_params(minval,maxval)

ot=backend_utils.OneTrough()
ot.set_params(minval,maxval)


x=np.arange(0,60)
y=[tp.generate(i) for i in x]
y2=[ot.generate(i) for i in x]

plt.scatter(x,y)
plt.scatter(x,y2)
plt.show()
