import sys

import cadquery as cq
import numpy as np
from stl import mesh


def roundvec(x):
    return np.round(x * 1000000.0) / 1000000.0


def read_stl(filename: str):
    input_mesh = mesh.Mesh.from_file(filename)
    return np.array([[roundvec(f) for f in e] for e in input_mesh.vectors])


def merge_poly(face_idx_lst, face_idx2edge_idx_lst):
    edge_idx_set = set()
    for f in face_idx_lst:
        for e in face_idx2edge_idx_lst[f]:
            if e not in edge_idx_set:
                edge_idx_set.add(e)
            else:
                edge_idx_set.remove(e)
    return edge_idx_set


def cluster_planes(faces_arr):
    a = faces_arr[:, 0, :]
    b = faces_arr[:, 1, :]
    c = faces_arr[:, 2, :]
    ab = b - a
    ac = c - a
    nrm = np.cross(ab, ac)
    nrm2 = nrm / np.linalg.norm(nrm, axis=1)[:, np.newaxis]
    dist = np.einsum("ij,ij->i", a, nrm2)
    v = roundvec(np.column_stack((nrm2, dist)))
    clust = {(e[0], e[1], e[2], e[3]): [] for e in v}
    for i, e in enumerate(v):
        if np.isnan(e[0]):
            continue
        clust[(e[0], e[1], e[2], e[3])].append(i)
    return list(clust.values())


def sort_edges(edges_merged):
    i = 0
    sorted_edges = []
    first_last = 0
    while True:
        current_edge = edges_merged.pop(i)
        sorted_edges.append(current_edge)
        current_pnt = current_edge[first_last]
        for i, e in enumerate(edges_merged):
            if current_pnt in e:
                first_last = 1 if e[0] == current_pnt else 0
                break
        else:
            break
    return sorted_edges


def match_points_of_faces(faces):
    pnt2face_idx_lst = {(f[0], f[1], f[2]): [] for e in faces for f in e}
    for i, e in enumerate(faces):
        for f in e:
            pnt2face_idx_lst[(f[0], f[1], f[2])].append(i)
    return list(pnt2face_idx_lst.keys()), list(pnt2face_idx_lst.values())


def invert_relation(relation, number_of_bins):
    inv_rel = [[] for i in range(number_of_bins)]
    for i, r in enumerate(relation):
        for e in r:
            inv_rel[e].append(i)
    return inv_rel


def find_edges_of_faces(face_idx2pnt_idx_lst):
    edge2faces_idx = {}
    for j, f in enumerate(face_idx2pnt_idx_lst):
        for i in range(len(f)):
            if f[i - 1] < f[i]:
                edge = (f[i - 1], f[i])
            elif f[i - 1] > f[i]:
                edge = (f[i], f[i - 1])
            else:
                print("edge with one point only")
                print((f[i - 1], f[i]))
                continue
                # raise BaseException("edge with one point only")

            if edge not in edge2faces_idx:
                edge2faces_idx[edge] = []
            edge2faces_idx[edge].append(j)
    return list(edge2faces_idx.keys()), list(edge2faces_idx.values())


def find_edges_of_polygons(polygons):
    edge2polygon_idx = {}
    for j, p in enumerate(polygons):
        for i in range(len(p)):
            edge = (p[i - 1], p[i])
            if edge not in edge2polygon_idx:
                edge2polygon_idx[edge] = []
            edge2 = (p[i], p[i - 1])
            if edge2 not in edge2polygon_idx:
                edge2polygon_idx[edge2] = []
            edge2polygon_idx[edge].append(j)
    return edge2polygon_idx


def merge_faces(faces_lst, face_idx2edge_idx_list, edge_idx2edge):
    edges_idx_merged_list = [
        list(merge_poly(f, face_idx2edge_idx_list)) for f in faces_lst
    ]
    edges_merged_list = [
        [edge_idx2edge[e] for e in edges_idx_merged]
        for edges_idx_merged in edges_idx_merged_list
    ]
    planes = []
    for edges_merged in edges_merged_list:
        sorted_edges_polygons = []
        while len(edges_merged) > 0:
            sorted_edges = sort_edges(edges_merged)
            sorted_edges_polygons.append(sorted_edges)
        planes.append(sorted_edges_polygons)
    planes_polygons_pts_idx = [
        [
            [
                (set(sorted_edges[i - 1]).intersection(set(sorted_edges[i]))).pop()
                for i in range(len(sorted_edges))
            ]
            for sorted_edges in sorted_edges_polygons
        ]
        for sorted_edges_polygons in planes
    ]
    return planes_polygons_pts_idx


def get_unclassified_faces(all_faces, classified_faces_lst):
    classified_faces = [f for m in classified_faces_lst for f in m]
    unclassified_faces = [
        e for i, e in enumerate(all_faces) if i not in classified_faces
    ]
    return unclassified_faces


def make_cq_poly_wire(poly_coords):
    wire = cq.Wire.makePolygon(
        [[c for c in poly_coords[i - 1]] for i in range(len(poly_coords))], close=True
    )
    return wire


# Thanks to CadQuery and OCCT: It works even with messed up outer <-> inner Wire. Even,
# if there are multiple outer wire (multiple polygons), it works, if they are
# fed to the inner Wires argument. The function definition shows, outer and
# inner Wire are just concatened to one list being analyzed and corrected by CadQuery or OCCT later.
#
# The orientation (concave or convex) of the faces doesn't need to be correct.
# It is also corrected by CadQuery of OCCT.
def make_cq_poly_faces(poly_coords):
    return [
        cq.Face.makeFromWires(
            make_cq_poly_wire(e[0]), [make_cq_poly_wire(f) for f in e[1:]]
        )
        for e in poly_coords
    ]


def count_len(lst):
    return np.unique(np.array([len(e) for e in lst]), return_counts=True)


if __name__ == "__main__":
    print("stl2step")

    # data input
    filename = sys.argv[1]
    print(f"Reading file: {filename}")
    faces = read_stl(filename)
    print(f"Number of input triangles: {len(faces):13d}")

    # prepare input data
    number_of_faces = faces.shape[0]
    pnts, pnt_idx2face_idx_lst = match_points_of_faces(faces)
    face_idx2pnt_idx_lst = invert_relation(pnt_idx2face_idx_lst, number_of_faces)
    edge_idx2edge, edge_idx2faces_idx = find_edges_of_faces(face_idx2pnt_idx_lst)
    face_idx2edge_idx_list = invert_relation(edge_idx2faces_idx, number_of_faces)

    # find planes
    faces_to_be_merged_list = cluster_planes(faces)
    print(f"Number of planes found: {len(faces_to_be_merged_list):16d}")
    unique, counts = count_len(faces_to_be_merged_list)
    for i, c in enumerate(unique):
        print(f"  with {c:6d} polygon{'s:' if c != 1 else ': '} {counts[i]:16d}")

    # construct polygons of planes
    polygons_pts_idx = merge_faces(
        faces_to_be_merged_list, face_idx2edge_idx_list, edge_idx2edge
    )

    # construct remaining unclassified triangles
    remaining_faces = get_unclassified_faces(
        face_idx2pnt_idx_lst, faces_to_be_merged_list
    )
    print(f"Number of remaining triangles: {len(remaining_faces):9d}")

    # build surface from planes and remaining triangles
    all_polygons = polygons_pts_idx + [[e] for e in remaining_faces]
    all_poly_coord = [
        [[pnts[pnt] for pnt in poly] for poly in plane] for plane in all_polygons
    ]
    cq_plane_faces = make_cq_poly_faces(all_poly_coord)

    shell = cq.Shell.makeShell(cq_plane_faces)
    output_filename = f"{filename[:-4]}.step"
    print(f"Writing file: {output_filename}")
    cq.exporters.export(shell, output_filename)
    print("Done.")
