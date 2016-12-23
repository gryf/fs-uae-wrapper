from unittest import TestCase
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

try:
    from unittest import mock
except ImportError:
    import mock

from fs_uae_wrapper import message


class TestMessage(TestCase):

    @mock.patch('multiprocessing.Process.start')
    def test_show(self, process_start):
        msg = message.Message('display that')
        msg.show()
        process_start.assert_called_once()

    def test_close(self):
        msg = message.Message('display that')
        msg._process = mock.MagicMock()
        msg._process.is_alive = mock.MagicMock(return_value=True)
        msg._process.terminate = mock.MagicMock()
        msg._process.join = mock.MagicMock()

        msg.close()
        msg._process.is_alive.assert_called_once()
        msg._process.terminate.assert_called_once()
        msg._process.join.assert_called_once()

        msg._process.is_alive = mock.MagicMock(return_value=False)
        msg._process.terminate.reset_mock()
        msg._process.join.reset_mock()

        msg.close()
        msg._process.is_alive.assert_called_once()
        msg._process.terminate.assert_not_called()
        msg._process.join.assert_called_once()


class TestSpawn(TestCase):

    @mock.patch('fs_uae_wrapper.message.MessageGui.__call__')
    def test_spawn(self, call):
        self.assertIsNone(message._spawn(''))
        call.assert_called_once()


class TestMessageGui(TestCase):

    def test_gui(self):
        msg = message.MessageGui(msg='display that')
        self.assertIsInstance(msg, tk.Tk)
        self.assertIsInstance(msg.frame, ttk.Frame)
        label = next(iter(msg.frame.children.values()))
        self.assertEqual(label.cget('text'), 'display that')

    @mock.patch('fs_uae_wrapper.message.tk.Tk.mainloop')
    def test_call(self, tkmain):
        msg = message.MessageGui(msg='display that')
        msg()
        tkmain.assert_called_once()
