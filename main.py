import numpy
import gmsh
import sys
import os
from airfoil_generator import calculate_airfoil

rotation = [90, 360, 0]

def create_dim_tags(dim, tags):
    dim_tags = []
    for tag in tags:
        dim_tags.append((dim, tag))
    return dim_tags

gmsh.initialize(sys.argv)

N = 50
A = 4
B = 4
TT = 12

x_points, z_points = calculate_airfoil(A, B, TT, N, 0.24)
zero_index = int(N/2) if N % 2 == 0 else int((N-1)/2)

def create_airfoil(x: list, z: list):
    tag_points_upper = []
    tag_points_lower = []
    for i in range(len(x_points)):
        p_i = gmsh.model.geo.add_point(x[i], 0, z[i])
        if i < zero_index:
            tag_points_upper.append(p_i)
        elif i > zero_index:
            tag_points_lower.append(p_i)
    tag_points_upper.append(zero_index + 1)
    tag_points_lower.insert(0, zero_index + 1)
    polyline_upper = gmsh.model.geo.add_polyline(tag_points_upper)
    polyline_lower = gmsh.model.geo.add_polyline(tag_points_lower)
    line_trailing_edge = gmsh.model.geo.add_line(tag_points_lower[-1], tag_points_upper[0])
    my_curve_loop = gmsh.model.geo.add_curve_loop([polyline_upper, polyline_lower, line_trailing_edge])
    gmsh.model.geo.add_plane_surface([my_curve_loop])

"""
def create_airfoil(x: list, z: list):
    tag_points = []
    tag_lines = []
    for i in range(len(x_points)):
        p_i = gmsh.model.geo.add_point(x[i], 0, z[i])
        tag_points.append(p_i)
    my_curve = gmsh.model.geo.add_line
    my_curve_loop = gmsh.model.geo.add_curve_loop(tag_lines)
    gmsh.model.geo.add_plane_surface([my_curve_loop])
"""

create_airfoil(x_points, z_points)

gmsh.model.geo.rotate([(2,1)], 0, 0, 0, 0, 1, 0, 35*numpy.pi/180)


# Linear Twist
gmsh.model.geo.twist([(2,1)], 0, 0, 0, 0, 0.9525, 0, 0, -1, 0, 25*numpy.pi/180)

# Discrete modelleme için
# TRY: Modeli occ kernelinde copy + translate(1e-3 maybe) + rotate(corresponding translate) + scale(if chord changes)
# şeklinde bir for döngüsü içinde yaz. Son oluşan yüzey harici hiçbirisini yüzey olarak tanımlama ama noktaları
# (get_boundary) sakla. Devamında noktaları spline (veya bspline, farklarını araştır) yardımıyla birleştir. Kanadın
# alt ve üst yüzeyini bu spline elemanların oluşturduğu curve loop ile oluştur (TE de aynı şekilde). Devamında meshing
# constraint olarak compound vermen gerekebilir (discrete point'lerden ötürü).

gmsh.model.geo.synchronize()


gmsh.option.set_number("General.Axes", 2)
gmsh.option.set_number("General.AxesMikado", 1)
gmsh.option.set_number("General.Trackball", 0)
gmsh.option.set_number("General.RotationX", rotation[0])
gmsh.option.set_number("General.RotationY", rotation[1])
gmsh.option.set_number("Geometry.Points", 0)
gmsh.option.set_number("Geometry.Surfaces", 1)
gmsh.fltk.run()

gmsh.finalize()