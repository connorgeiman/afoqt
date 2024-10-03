import vtkplotlib as vpl
import vtk
from stl.mesh import Mesh
import numpy as np

# Use this script once to generate all the jet images in /3_jets

clean_stl = "instrument_comprehension/3_jets/F-35.stl"

horizons_pitch = [0,0,0,30,30,30,-30,-30,-30,10,10]
horizons_roll = [0,-45,45,0,-45,45,0,-45,45,-90,90]
compass_headings = [0,-45,-90,-135,-180,135,90,45]

for i in range(len(compass_headings)):
    for j in range(len(horizons_pitch)):
        image_name = f"jet_{j+1}-{i+1}.png"

        # Load STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(clean_stl)
        reader.Update()

        # Create transformation matrix to rotate STL file
        transform = vtk.vtkTransform() 
        transform.RotateY(compass_headings[i])
        transform.RotateX(horizons_pitch[j])
        transform.RotateZ(horizons_roll[j])

        # Apply transformation to STL file
        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(reader.GetOutputPort())
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        # Write transformed STL file to disk
        writer = vtk.vtkSTLWriter()
        writer.SetFileName("instrument_comprehension/3_jets/F-35_rotated.stl")
        writer.SetInputConnection(transform_filter.GetOutputPort())
        writer.Write()

        # Read the STL using numpy-stl
        path = "instrument_comprehension/3_jets/F-35_rotated.stl"
        mesh = Mesh.from_file(path)

        # Plot the mesh
        vpl.mesh_plot(mesh, color='grey')

        vpl.view()

        # Save the figure as a PNG file
        vpl.save_fig(image_name,off_screen=True)
        
        vpl.close()