import cloudvolume
import json
import pandas as pd
from matplotlib import pyplot as plt
# from neuron import h, gui
from morphio import Option
from morphio.mut import Morphology
from morphio import PointLevel, SectionType, Option
import numpy as np

# h.load_file('stdrun.hoc')
# h.load_file('import3d.hoc')

c3_cloudvolume = cloudvolume.CloudVolume('gs://h01-release/data/20210601/c2', progress=True)
# c3_cloudvolume = cloudvolume.CloudVolume('gs://h01-release/data/20210601/blood_vessels_segments', progress=True)

data = json.load(open('metadata.json','r'))

# put the metadata into a DataFrame
mydata = {'ids':data['inline']['ids']}
for i,tag in enumerate(data['inline']['properties'][0]['tags']):
  mydata[tag] = [i in tags for tags in data['inline']['properties'][0]['values']]
for i in range(1,len(data['inline']['properties'])):
  mydata[data['inline']['properties'][i]['description']] = data['inline']['properties'][i]['values']
metadata = pd.DataFrame.from_dict(mydata)
metadata = metadata.set_index('ids')

pyrcells = metadata[metadata['pyramidal']]
pyrcells.head()

skel = c3_cloudvolume.skeleton.get(int(pyrcells.iloc[2].name))

soma_ind = np.argmax(skel.radii)
ind = 0
edge = skel.edges[ind]
while soma_ind not in edge:
  ind = ind + 1
  edge = skel.edges[ind]

morpho = Morphology()
sections = {}
sections[skel.edges[ind][1]] = morpho.append_root_section(
        PointLevel(
        [list(skel.vertices[i]) for i in skel.edges[ind]],  # x, y, z coordinates of each point
        [2*skel.radii[i] for i in skel.edges[ind]]),  # diameter of each point
        SectionType.undefined)

for edge_ind, edge in enumerate(skel.edges[ind+1:]):
  if edge[0] in sections:
    sections[edge[1]] = sections[edge[0]].append_section(
      PointLevel(
          [list(skel.vertices[i]) for i in edge],
          [2*skel.radii[i] for i in edge]),
          SectionType.undefined)
#   else:
#     print(edge)
#     sections[edge[1]] = morpho.append_root_section(
#         PointLevel(
#           [list(skel.vertices[i]) for i in edge],
#           [2*skel.radii[i] for i in edge]),
#           SectionType.undefined)

# for ei in range(ind-1, -1, -1):
#   edge = skel.edges[ei]
#   if edge[0] in sections:
#     sections[edge[1]] = sections[edge[0]].append_section(
#       PointLevel(
#           [list(skel.vertices[i]) for i in edge],
#           [2*skel.radii[i] for i in edge]),
#           SectionType.undefined)
#   else:
#     print(edge)
#     sections[edge[1]] = morpho.append_root_section(
#         PointLevel(
#           [list(skel.vertices[i]) for i in edge],
#           [2*skel.radii[i] for i in edge]),
#           SectionType.undefined)

# morpho.remove_unifurcations()
# morpho.write("swcs/pyr_2_startAtSoma_v5.swc")


# point_ind = ind + 1
# while point_ind < len(skel.edges):
#     edge = skel.edges[point_ind]
#     if edge[0] in sections:

#         sections[edge[1]] = sections[edge[0]].append_section(
#         PointLevel(
#             [list(skel.vertices[i]) for i in edge],
#             [2*skel.radii[i] for i in edge]),
#             SectionType.undefined)
#         point_ind = point_ind + 1
#     else:
#         print(edge)
#         sections[edge[1]] = morpho.append_root_section(
#             PointLevel(
#             [list(skel.vertices[i]) for i in edge],
#             [2*skel.radii[i] for i in edge]),
#             SectionType.undefined)
#         point_ind = point_ind + 1

# point_ind = soma_ind - 1
# while point_ind >= 0:
#     edge = list(skel.edges[point_ind])
#     edge.reverse()
#     if edge[0] in sections:
#         sections[edge[1]] = sections[edge[0]].append_section(
#         PointLevel(
#             [list(skel.vertices[i]) for i in edge],
#             [2*skel.radii[i] for i in edge]),
#             SectionType.undefined)
#         point_ind = point_ind - 1
#     else:
#         print(edge)
#         sections[edge[1]] = morpho.append_root_section(
#             PointLevel(
#             [list(skel.vertices[i]) for i in edge],
#             [2*skel.radii[i] for i in edge]),
#             SectionType.undefined)
#         point_ind = point_ind - 1
# sections[skel.edges[0][1]] = morpho.append_root_section(
#     PointLevel(
#         [list(skel.vertices[i]) for i in skel.edges[0]],  # x, y, z coordinates of each point
#         [2*skel.radii[i] for i in skel.edges[0]]),  # diameter of each point
#         SectionType.undefined)