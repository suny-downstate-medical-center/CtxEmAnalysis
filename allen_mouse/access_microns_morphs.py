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
import neuprint

client = CAVEclient("minnie65_public_v117")
example_cell_id = 864691135474648896

# to enable a cache, create a MeshMeta object
mm = trimesh_io.MeshMeta(
    cv_path=client.info.segmentation_source(),
    disk_cache_path="minnie65_v117_meshes",
    map_gs_to_https=True,
)

mesh = mm.mesh(seg_id=example_cell_id)

## smoothing
new_verts = skeletonize.smooth_graph(
    mesh.vertices, mesh.graph_edges, neighborhood=1, r=0.1, iterations=100
)
mesh.vertices = new_verts
# mesh.fix_mesh(verbose=True)
skel = skeletonize.skeletonize_mesh(mesh)
# skel.export_to_swc("example.swc")


### Some function to make use of neuprint
def skel_to_df(skel):
    """convert the skel into a DataFrame that can be used with neuprint"""
    rows = [
        {"rowId": i, "x": x, "y": y, "z": z, "radius": r, "link": -1}
        for (i, (x, y, z)), r in zip(enumerate(skel.vertices), skel.radius)
    ]
    for a, b in skel.edges:
        if rows[a]["link"] != -1:
            print("two parent sections!")
        rows[a]["link"] = b
    return pd.DataFrame(rows)


def traverse(rowId, edges):
    """depth first traversal of the cell keeping track of the node id
    and parents"""
    stack = []
    pstack = []
    rowOrder = []
    parents = [-1]
    while True:
        rowOrder.append(rowId)
        if rowId in edges and len(edges[rowId]) > 0:
            child = edges[rowId].pop(0)
            stack.extend(edges[rowId])
            parent = len(rowOrder) - 1
            pstack.extend([parent for i in edges[rowId]])
            parents.append(parent)
            rowId = child
        elif stack == []:
            break
        else:
            rowId = stack.pop(0)
            parents.append(pstack.pop(0))
    return rowOrder, parents


def skel_sort(df):
    """order the nodes so the parent is always before the child in the tree"""
    edges = {}
    for r, l in zip(df.rowId, df.link):
        if l in edges:
            edges[l].append(r)
        else:
            edges[l] = [r]
    nd = df[df.link == -1]
    rowOrder, links = traverse(nd.rowId[0], edges)
    df.loc[rowOrder, "rowId"] = range(len(rowOrder))
    df.loc[rowOrder, "link"] = links
    df.sort_values("rowId", inplace=True)
    df.index = df.rowId


# Try neuprint to 'heal' the morphology
skel_df = skel_to_df(skel)
heal_df = neuprint.skeleton.heal_skeleton(skel_df)
skel_sort(heal_df)
neuprint.skeleton.skeleton_df_to_swc(heal_df, export_path="example_heal.swc")
