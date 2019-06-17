import unittest 

from selfosc.delay_lines import DelayLine

class testDelayLine(unittest.TestCase):
    def test_delay_line_create(self):
        dl = DelayLine()

    def test_read_sample_at(self):
        n_samp = 10
        dl = DelayLine(n_samp)
        for ii in range(n_samp):
            dl.insert_sample(ii)
        dldump = dl.dump_line()
        for ii in range(n_samp):
            self.assertEqual(dl.read_delay(ii), dldump[ii])

    def test_delay_is_right(self):
        n_samp = 3
        dl = DelayLine(n_samp)
        sampl_count = 0
        for ii in range(n_samp):
            dl.insert_sample(sampl_count)
            sampl_count += 1
        for ii in range(3*n_samp):
            dl.insert_sample(sampl_count)
            self.assertEqual(dl.read_delay(), sampl_count-n_samp)
            sampl_count += 1

    def test_zero_delay_read(self):
        n_samp = 3
        dl = DelayLine(n_samp)
        sampl_count = 0
        for ii in range(n_samp*2):
            dl.insert_sample(sampl_count)
            self.assertEqual(dl.read_delay(0), sampl_count+0.)
            sampl_count += 1


if __name__ == '__main__':
    unittest.main()
