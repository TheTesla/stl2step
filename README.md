# Intelligent conversion from STL to STEP

This cli program converts STL files into STEP file in a non-trivial way. It segments the mesh into basic shapes. That means, the generated STEP file isn't only a bunch of triangles, it has planes, cylinders, spheres etc. resulting in less memory usage and it is friendlier to CAD and CAM. 

Experimental state: Only planes are implemented! Holes are not supported!

![screenshot of the output screw.step imported into FreeCAD](screw_step.png)


## Usage

```bash
python3 stl2step myfile.stl
```

The out file is named similar to the input file: `myfile.step`, because it only replaces `.stl` with `.step`.

## Autor

Stefan Helmert <stefan@entroserv.de>

## License

AGPL v3



