import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

class BimodalSim:
    def __init__(self,df,target_min,target_max,noise_scale=0.25, inverse=False):
        self.df=df
        x = df['time']
        y = df['value']

        y=y/np.max(y)

        if inverse:
            y=1/y

        self.base_min=np.min(y)
        self.base_max=np.max(y)

        self.target_min=target_min
        self.target_max=target_max

        self.f = interp1d(x, y, kind='cubic')
        self.noise_range=(target_max-target_min)*noise_scale

    def generate(self,x):
        val=self.f(x)
        noise=np.random.uniform(-self.noise_range/2, self.noise_range,1).item()
        val+=noise
        val=max(val,0)
        return val

lower_bound=10
upper_bound=20

df=pd.read_csv("../data/bimodal_dist.csv")

sim=BimodalSim(df,lower_bound,upper_bound,inverse=True)

x=np.linspace(1,24,1440)
y=[sim.generate(i) for i in x]

plt.plot(x,y)
plt.show()










