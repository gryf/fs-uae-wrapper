from unittest import TestCase

from fs_uae_wrapper import path


class TestPath(TestCase):

    def test_which(self):
        self.assertEqual(path.which('sh'), 'sh')
        self.assertIsNone(path.which('blahblahexec'))
        self.assertEqual(path.which(['blahblahexec', 'pip', 'sh']),
                         'pip')
