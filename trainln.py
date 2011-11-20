import numpy as np
from neurolab.core import Train, Trainer, TrainStop
from neurolab import *

class TrainLM(Train):
    ''' The training class using Levenberg-Marquardt and the neurolab-package'''
    def __init__(self, net, input, target, **kwargs):
        self.net = net
        self.input = input
        self.target = target
        self.kwargs = kwargs
        self.x = tool.np_get_ref(net)
        self.full_output = ()
    
    def fcn(self, x):
        self.x[:] = x
        output = net.sim(self.input)
        err = self.error(self.net, self.input, self.target, output)
        try:
            self.epochf(err, self.net)
        except TrainStop:
            pass
        return (self.target-output).flatten()
        
    def __call__(self, net, input, target):
        from scipy.optimize import leastsq
        from scipy.optimize.minpack import error
        
        self.full_output = leastsq(func=self.fcn, x0=self.x.copy(), 
                                    maxfev=self.epochs)

