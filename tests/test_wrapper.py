import os
from tempfile import mkstemp
from unittest import TestCase


from fs_uae_wrapper import wrapper


class TestWrapper(TestCase):

    def setUp(self):
        fd, self.fname = mkstemp()
        os.close(fd)

    def tearDown(self):
        os.unlink(self.fname)

    def test_get_wrapper_from_conf_positive(self):

        configs = ["[conf]\nwrapper=foo\n",
                   "[conf]\n wrapper =foo\n",
                   "[conf]\n wrapper =    foo\n",
                   "[conf]\nwrapper = foo    \n"]

        for cfg in configs:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertEqual(val, 'foo')

    def test_get_wrapper_from_conf_negative(self):

        configs = ["[conf]\nwraper=foo\n",
                   "[conf]\nwrapper\n",
                   "[conf]\nfullscreen = 1\n"]

        for cfg in configs:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertIsNone(val)

        configs2 = [("[conf]\nwrapper= = = something went wrong\n",
                     "= = something went wrong"),
                    ("[conf]\nwrapper = =    \n", "="),
                    ("[conf]\nwrapper =     \n", "")]
        for cfg, result in configs2:
            with open(self.fname, 'w') as fobj:
                fobj.write(cfg)

            val = wrapper.get_wrapper_from_conf(self.fname)
            self.assertEqual(val, result)
