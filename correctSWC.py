# generate dict of points 
import pandas as pd 
import numpy as np 

def isterminal(df, p):
    nextgen = df[df['point'] == p].children.values[0]
    decendents = df[df['point'] == p].children.values[0]
    count = 0
    while 1 not in decendents and count <= len(df):
        kids = []
        for p in nextgen:
            kids.extend(df[df['point'] == p].children.values[0])
        decendents.extend(kids)
        nextgen = kids 
        count = count + 1
    if 1 in decendents:
        return False
    else:
        return True 

# fin = open('pyr_2.swc', 'r')
fin = open('allen_mouse/smoothed_example.swc')
# fout = open('pyr_4_corrected.swc', 'w')
points = {'point' : [], 'type' : [], 'x' : [], 'y' : [], 'z' : [],
        'radius' : [], 'parent' : []}
count = 0
while True:
    line = fin.readline()
    if not line:
        break
    typ = True
    x = False
    y = False
    z = False
    diam = False 
    parent = False 
    if count >= 0:
        linesplit = line.split(' ')
        points['point'].append(int(linesplit[0]))
        for l in linesplit[1:]:
            if l != '':
                if typ:
                    points['type'].append(int(l))
                    typ = False
                    x = True 
                elif x:
                    points['x'].append(float(l))
                    x = False
                    y = True 
                elif y:
                    points['y'].append(float(l))
                    y = False
                    z = True 
                elif z:
                    points['z'].append(float(l))
                    z = False
                    diam = True 
                elif diam:
                    points['radius'].append(float(l))
                    diam = False
                    parent = True
                elif parent:
                    points['parent'].append(int(l.split("\n")[0]))
                    parent = False 
                    typ = True
    count = count + 1
fin.close()

df = pd.DataFrame(points)

children = []
for p in df['point']:
    kids = df[df['parent'] == p]
    children.append(list(kids['point'].values))

df['children'] = children

noparent = df[df['parent'] == -1]['point'].values[1:]
newpairs = {'point' : [], 'parent' : []}
for point in noparent:
    # print('point: %i' % (point))
    # if not isterminal(df, point):
    #     print('Not Terminal')
    others = df[df['point'] != point]

    dists = np.sqrt((np.square(np.subtract(others['x'].values, df[df['point'] == point]['x'].values))
            + np.square(np.subtract(others['y'].values, df[df['point'] == point]['y'].values))
            + np.square(np.subtract(others['z'].values, df[df['point'] == point]['z'].values))))

    sortinds = np.argsort(dists)
    for ind in sortinds:
        id = others['point'].values[ind]
        # print('trying %i' % id)
        if not len(others[others['point'] == id].children.values[0]):
            break

    newpairs['point'].append(point)
    newpairs['parent'].append(id)
    # print('\n')
for point, parent in zip(newpairs['point'], newpairs['parent']):
    print('%i to %i' % (point, parent))

# write new swc 
fout = open('allen_mouse/smoothed_example_corrected.swc', 'w')
for datum in df.iloc:
    if datum['point'] in noparent:
        l = '%i %i %f %f %f %f' % (
            datum['point'], datum['type'], datum['x'], datum['y'],
            datum['z'], datum['radius']
        )
        parent = newpairs['parent'][np.argwhere(np.array(newpairs['point']) == datum['point'])[0][0]]
        l = l + ' ' + str(parent)
    else:
        l = '%i %i %f %f %f %f %i' % (
            datum['point'], datum['type'], datum['x'], datum['y'],
            datum['z'], datum['radius'], datum['parent']
        )
    fout.write(l + '\n')
fout.close()



# # for unconnected points get distance distance to other
# for point in points:
#      if point is not 1:
#          if points[point]['parent'] == -1:
#             dists = []
#             ids = []
#             for other in points:
#                 if other is not point:
#                     dists.append(((points[other]['x'] - points[point]['x'])**2 
#                         + (points[other]['y'] - points[point]['y'])**2 
#                         + (points[other]['z'] - points[point]['z'])**2)**(0.5))
#                     ids.append(other)
                    





#     if '-1' in line and count:
#         elements = line.split(' ')
#         id = int(elements[0])
#         parent = id -1 
#         newline = str(id) + ' '
#         for element in elements[1:-1]:
#             newline = newline + element + ' '
#         newline = newline + str(parent) + '\n'
#         count = count + 1
#     elif '-1' in line:
#         newline = line 
#         count = count +1
#     else:
#         newline = line
#     fout.write(newline)

# fin.close()
# fout.close()
