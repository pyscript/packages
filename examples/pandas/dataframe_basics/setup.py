"""
Shim IPython's display API onto PyScript so example code written in a
Jupyter/IPython idiom runs unmodified in the browser.

After this module executes, both of the following imports work in example
code and resolve to the PyScript equivalents:

    from IPython.core.display import display, HTML
    from IPython.display import display, HTML
"""

import sys
import types
from pyscript import HTML, display


# Standard dynamic module creation and registration in sys.modules to shim
# IPython's display API onto PyScript. ;-)
ipython = types.ModuleType("IPython")
core = types.ModuleType("IPython.core")
core_display = types.ModuleType("IPython.core.display")
core_display.display = display
core_display.HTML = HTML
ipython.core = core
core.display = core_display
# Libraries like matplotlib check for IPython by doing
# `sys.modules.get("IPython").get_ipython()` and expect either a shell
# object or None. We don't have a shell object, but we can at least return
# None to avoid errors.
ipython.get_ipython = lambda: None
# IPython.display is also a common import path, so we also register that.
ipython.display = core_display
# Register the modules in sys.modules so they can be imported by the example
# Python in code.py.
sys.modules["IPython"] = ipython
sys.modules["IPython.core"] = core
sys.modules["IPython.core.display"] = core_display
sys.modules["IPython.display"] = core_display
# That's it!