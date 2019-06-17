"""
  simple_delay_tubes.py

  provides simple delay lines that can be plugged together
"""

import numpy as np

from .delay_lines import DelayLine

class Tube(object):
    """
    Class for a straight tube described by a single pair of delay lines

    This object is described by two integer delay lines, one for
    incoming waves and another for outgoing ones.

    Provides methods to read the two state variables
    (pressure and flow in the case of an air resonator)
    These variables correspond to the sum and difference
    of the two delay lines

    Parameters
    ----------
    delay : int
            the delay of the tube from one end to the other
            (proportional to the length of the tube)

    losses : float
             Each sample propagation losses a small fraction of
             its amplitude
    """
    def __init__(self, delay=1, losses=0.):
        self.extra = 5
        self.dlin = DelayLine(delay, extra=self.extra)
        self.dlout = DelayLine(delay, extra=self.extra)
        # scattering matrix (unused?)
        self.scat = None
        self.tube_l = None
        self.tube_r = None
        self.delay = delay
        # Attenuation for the entire delay line
        self.prop_mult = (1-losses)**delay
        # Attenuation for a single sample
        self.smpl_prop_mult = 1-losses

    def insert_incoming_sample(self, sin):
        """
        inserts one sample in the incoming delay line

        Parameters
        ----------
        sin : float
              New sample
        """
        self.dlin.insert_sample(sin)

    def insert_outgoing_sample(self, sin):
        """
        inserts one sample in the outgoing delay line

        Parameters
        ----------
        sin : float
              New sample
        """
        self.dlout.insert_sample(sin)

    def read_outgoing(self):
        """
        Reads one sample from the outgoing delay line at its exit point
        The sample is attenuated according to the tube losses

        Parameters
        ----------
        None
        """
        # This should be the out delay, -2 is some weird correction
        return self.dlout.read_delay(self.dlout.delay-2)*self.prop_mult

    def read_incoming(self):
        """
        Reads one sample from the incoming delay line at its exit point
        The sample is attenuated according to the tube losses

        Parameters
        ----------
        None
        """
        # This should be the in delay, -2 is some weird correction
        return self.dlin.read_delay(self.dlin.delay-2)*self.prop_mult

    def read_samples(self):
        """
        Reads samples from both delay lines at their exit points
        Samples are attenuated according to the tube losses

        Parameters
        ----------
        None

        Returns
        -------
        outgoing_sample, incoming_sample
        """
        return self.read_outgoing(), self.read_incoming()

    def read_incoming_at_pos(self, index):
        """
        Reads one sample from incoming delay line at position index

        Parameters
        ----------
        index : int
                distance in samples from input of the tube
        """
        return self.dlin.read_delay(self.delay-index)*(self.smpl_prop_mult)**(self.delay-index)

    def read_outgoing_at_pos(self, index):
        """
        Reads one sample from outgoing delay line at position index

        Parameters
        ----------
        index : int
                distance in samples from input of the tube
        """
        return self.dlout.read_delay(index)*(self.smpl_prop_mult)**(index)

    def get_sum_at_pos(self, index):
        """
        Returns the sum (pressure) at position given by `index`

        Parameters
        ----------
        index : int
                distance in samples from input of the tube
        """
        #pini = self.dlin.read_delay(self.delay-index)
        #pouti = self.dlout.read_delay(index)
        pini = self.read_incoming_at_pos(index)
        pouti = self.read_outgoing_at_pos(index)
        return pini + pouti

    def get_diff_at_pos(self, index):
        """
        Returns the difference (pressure) at position given by `index`

        Parameters
        ----------
        index : int
                distance in samples from input of the tube
        """
        pini = self.dlin.read_delay(self.delay-index)
        pouti = self.dlout.read_delay(index)
        return -pini + pouti

    def get_sum_distribution(self):
        """
        Returns the sum (pressure) in the entire tube

        Parameters
        ----------
        None

        Returns
        ------
        vector with pressure (index 0 == tube input)
        """
        pmults = self.smpl_prop_mult**np.arange(self.delay+1)
        pout = np.array(self.dlout.dump_line())*pmults
        pin = np.flipud(np.array(self.dlin.dump_line())*pmults)
        return pout+pin


class TubeAssembly(object):
    """
    An assembly of tubes with varying lengths and diameters

    Provides the scattering matrices used to calculate reflection and
    transmission coefficients from one tube to the next, and reflection at end

    Parameters
    ----------
    None

    Example
    -------
    >>> ta = TubeAssembly()
    >>> ta.append_tube(length=10, radius=0.1, losses=0.001)

    Creates the tube assembly instance and adds one tube
    """

    def __init__(self):
        self.tubes = []
        self.scats = []
        self.radii = []

    def append_tube(self, delay=1, radius=1., losses=0.):
        """
        Appends one tube to the tube assembly at the end of the last tube

        Parameters
        ----------

        delay : int
                Tube length in samples
        radius : float
                 tube radius (only relative units are relevant)
        losses : float
                 fraction of the amplitude that is lost per sample in the tube

        """
        self.tubes.append(Tube(delay=delay, losses=losses))
        # default scattering junction: perfect open pipe
        self.scats.append(np.array([[0, 1], [-1, 0]]))
        self.radii.append(radius)
        self.connect_tubes()

    def connect_tubes(self, index=-1):
        """
        Calculates the scattering matrices for between two tubes

        (callesd by append_tube())

        Parameters
        ----------

        index : int
                index of the tube into which the new matrix is calculated
                (refers to scattering between tube index-1 and index
        """
        if index < 0:
            index = len(self.tubes)+index
        if index == 0:
            return
        # scalers (proportional to zc)
        scr = 1/self.radii[index]**2
        scl = 1/self.radii[index-1]**2
        newscat = np.array([[2*scr, scl-scr],
                            [scr-scl, 2*scl]])/(scr+scl)
        self.scats[index-1] = newscat

    def scatter(self, index, outgoing_val=0.0, incoming_val=0.0):
        """
        inserts outgoing (from left) value and incoming (from right)
        into the cattering junction and returns

        Parameters
        ----------

        outgoing : float
                  (into right) and
        incoming : float
                  (into left) values
        """
        scat = self.scats[index]
        plout_refl = outgoing_val*scat[1, 0]
        plout_trans = outgoing_val*scat[0, 0]
        prin_trans = incoming_val*scat[1, 1]
        prin_refl = incoming_val*scat[0, 1]
        return prin_refl+plout_trans, prin_trans+plout_refl

    def insert_values(self, val, ret_val=0.0):
        """
        insert a new value at the tube start, and advance
        all the delay lines

        optionally insert a value at the end of the tube (0 by default)


        Parameters
        ----------
        val : float
              New value into tube start
        ret_val : float
                  New value into tube end

        Returns
        -------

        outgoing value from the radiative end
        """
        # insert in first tube
        #self.tubes[0].insert_outgoing_sample(val)
        # propagate outwards
        prev_prout = val
        for ii, tube in enumerate(self.tubes[:-1]):
            plout = self.tubes[ii].read_outgoing()
            prin = self.tubes[ii+1].read_incoming()
            prout, plin = self.scatter(ii, plout, prin)
            self.tubes[ii].insert_incoming_sample(plin)
            self.tubes[ii].insert_outgoing_sample(prev_prout)
            prev_prout = prout
        # last element
        plout = self.tubes[-1].read_outgoing()
        prin = ret_val
        prout, plin = self.scatter(len(self.scats)-1, plout, prin)
        self.tubes[-1].insert_incoming_sample(plin)
        self.tubes[-1].insert_outgoing_sample(prev_prout)

        return prout

    def get_sum_distribution(self):
        """
        Returns a vector with sum (pressure) along the entire tube
        """
        ps = np.zeros(sum(tt.delay for tt in self.tubes)+1)
        pos = 0
        for tt in self.tubes:
            ps[pos:pos+tt.delay+1] += tt.get_sum_distribution()
            pos += tt.delay
        return ps

    def get_incoming_pressure_at_start(self):
        """
        Returns the incoming pressure at the input (active) end
        of the complete resonator
        """
        return self.tubes[0].read_incoming_at_pos(0)

    def get_tube_at_pos(self, index):
        """
        return the tube corresponding to position 
        """
        pos = 0

        for ii, tt in enumerate(self.tubes):
            prev_pos = pos
            pos += tt.delay
            if pos >= index:
                return tt, index-prev_pos

    def get_sum_at_pos(self, index):
        """
        Return the sum of delay lines at position (0=tube entrance)
        """
        tube, tube_pos = self.get_tube_at_pos(index)
        return tube.get_sum_at_pos(tube_pos)

