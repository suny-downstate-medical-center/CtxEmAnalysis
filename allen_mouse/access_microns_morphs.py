import cloudvolume
import json
import pandas as pd
from matplotlib import pyplot as plt
# from neuron import h, gui
from morphio import Option
from morphio.mut import Morphology
from morphio import PointLevel, SectionType, Option
import numpy as np
from meshparty import trimesh_io, trimesh_vtk
from caveclient import CAVEclient
from meshparty import skeletonize

client = CAVEclient('minnie65_public_v117')
example_cell_id = 864691135474648896

# to enable a cache, create a MeshMeta object
mm = trimesh_io.MeshMeta(cv_path = client.info.segmentation_source(),
                         disk_cache_path='minnie65_v117_meshes',
                         map_gs_to_https=True)

mesh = mm.mesh(seg_id=example_cell_id)

## smoothing
new_verts = skeletonize.smooth_graph(mesh.vertices,
                                     mesh.graph_edges,
                                     neighborhood=1,
                                     r=.1,
                                     iterations=100)
mesh.vertices = new_verts
# mesh.fix_mesh(verbose=True)
skel = skeletonize.skeletonize_mesh(mesh)
skel.export_to_swc('example.swc')
# morpho = Morphology()
# sections = {}

# for edge in mesh.edges():
#   if edge[0] in sections:
#     sections[edge[1]] = sections[edge[0]].append_section(
#       PointLevel(
#           [list(mesh.vertices[i]) for i in edge],
#           [2*mesh.radii[i] for i in edge]),
#           SectionType.undefined)
#   else:
#     print(edge)
#     sections[edge[1]] = morpho.append_root_section(
#         PointLevel(
#           [list(mesh.vertices[i]) for i in edge],
#           [2*mesh.radii[i] for i in edge]),
#           SectionType.undefined)
# morpho.remove_unifurcations()
#morpho.write("/drive/MyDrive/outfile.swc")