"""Apply the packaged Battlezone tool icon to Windows Tk windows."""
import os
import sys

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "GrizzlyOne95.Battlezone98Redux.LocalizationTool"
        )
    except Exception:
        pass

    try:
        import tkinter as tk

        icon_path = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "bzlocal.ico")
        if os.path.exists(icon_path):
            def _wrap_init(cls):
                original = cls.__init__
                def wrapped(self, *args, **kwargs):
                    original(self, *args, **kwargs)
                    try:
                        self.iconbitmap(icon_path)
                    except Exception:
                        pass
                cls.__init__ = wrapped

            _wrap_init(tk.Tk)
            _wrap_init(tk.Toplevel)
    except Exception:
        pass
