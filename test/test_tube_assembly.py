import unittest 

from selfosc.simple_delay_tubes import TubeAssembly

class testDelayLine(unittest.TestCase):
    def test_tube_assembly_create(self):
        ta=TubeAssembly()

    def test_single_tube_delay(self):
        ta=TubeAssembly()
        delay = 3
        val = .9
        ta.append_tube(delay=delay, radius=1.0)
        ta.insert_values(val)
        for ii in range(3*delay):
            inval = ta.get_incoming_pressure_at_start()
            ta.insert_values(0.0)
            if inval == -val:
                print('Value arrived at sample {} (tub delay={})'.format(ii,delay))
            else:
                self.assertEqual(inval,0.0)

if __name__ == '__main__':
    unittest.main()
