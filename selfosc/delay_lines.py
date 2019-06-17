
import numpy as np

class DelayLine(object):
    def __init__(self, delay=1, extra=1):
        """
        initalise a delay line with maximum delay "delay"

        Parameters
        ----------
        delay : int
                Maximum expeceted delay in samples
        extra : int
                Extra samples to include
                ( for example if a filter is to be included)
        """
        # n_samp is the total number of samples to be kept in mem
        n_samp = delay + extra
        self.line = np.zeros(n_samp)
        # ptr points to the last inserted sample
        self.ptr = 0
        self.n_samp = n_samp
        self.delay = delay
        # n ticks is the number of inserted samples since beginning
        # (mostly for debugging)
        self.nticks = 0

    def increase_ptr(self):
        """
        increase the pointer by one sample

        Should not be called by user, 'insert_sample' calls this
        """
        self.ptr += 1
        if self.ptr > len(self.line)-1:
            self.ptr = 0
        self.nticks += 1

    def insert_sample(self, sin):
        """
        Inserts one sample and advances pointer
        """
        #self.line[(self.ptr+1)%self.n_samp] = sin
        self.increase_ptr()
        self.line[self.ptr] = sin

    def read_delay(self, delay=None):
        """
        Read the delayed sample at a particular position

        Parameters
        ----------

        delay : int
                read at delay samples from current pointer
                By default this is the maximum delay defined at init
        """
        if delay is None:
            delay = self.delay
        return self.line[(self.ptr-delay)%self.n_samp]

    def dump_line(self):
        """
        Read the entire delay line from current sample to maximum delay
        """
        rolled_line = np.roll(np.flipud(self.line), self.ptr+1)
        return (rolled_line)[:self.delay]

    def __getitem__(self, index):
        return self.line[index]

