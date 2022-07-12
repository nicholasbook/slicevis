## slicevis
---
A Python package for interactive slice visualization of 3D datasets in Jupyter notebooks.

# Installation (Windows)
1. Clone this repository `git clone https://git.rwth-aachen.de/nicholasbook/sce-project-ss22.git`.
2. (Optional) Create a virtual environment `py -m venv env` and activate it `call env/Scripts/activate.bat`.
3. Install locally using `pip install -e .`

# Usage
*slicevis* is meant to be used in combination with Jupyter notebooks. I recommend you use VSCode with the Python and Jupyter extension installed.
Check out the `examples` directory for test data and prepared notebooks.

Minimal usage:
`from slicevis import SliceWidget`
`data = slicevis.load_image("CT280.gff")`
`widget = slicevis.SliceWidget(data.get_timepoint())` 

# License
The *slicevis* package is licensed under the term of the MIT license.

The examples directory of this repository contain data that is licensed under CC-BY-SA 4.0. Please refer to `examples/LICENSE.txt` for more details.
