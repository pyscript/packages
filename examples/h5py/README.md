# h5py Examples

Each sub-directory contains a self-contained example. The order in
which the examples are to appear is specified in `order.json` (an
array of directory names in the expected order).

In each example directory you'll find:

* `config.toml` - must conform to the specification outlined here:
  https://docs.pyscript.net/latest/user-guide/configuration/ This is
  parsed and ultimately turned into a JSON representation as part of
  the package's API object.
* `setup.py` - Python code for contextual and environmental setup,
  NOT SEEN BY THE END USER, but is run before the `code.py` code is
  evaluated. Allows us to create useful (IPython) shims, avoid
  repeating boilerplate and whatnot.
* `code.py` - the actual code added to the editor which forms the
  practical example of using the package.
