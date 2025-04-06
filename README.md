<!--
SPDX-FileCopyrightText: 2025 Stefan Helmert <stefan@entroserv.de>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Intelligent conversion from STL to STEP

This cli program converts STL files into STEP file in a non-trivial way. It segments the mesh into basic shapes. That means, the generated STEP file isn't only a bunch of triangles, it has planes, cylinders, spheres etc. resulting in less memory usage and it is friendlier to CAD and CAM. 

Experimental state: Only planes are implemented! Holes __are__ supported now!

![screenshot of the output step file imported into FreeCAD and the conversion log](example_step.png)


## Installation

```bash
pip3 install stl2step
```

## Usage

```bash
python3 -m stl2step myfile.stl
```

The out file is named similar to the input file: `myfile.step`, because it only replaces `.stl` with `.step`.

## Autor

Stefan Helmert <stefan@entroserv.de>

## License

AGPL v3



