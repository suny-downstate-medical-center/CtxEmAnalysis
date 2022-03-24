from posixpath import split
# import cloudvolume
import json
import pandas as pd
import numpy as np 
from os import listdir
from avro.datafile import DataFileReader
from avro.io import DatumReader
from matplotlib import pyplot as plt
import multiprocessing

# metadata = pd.read_pickle('h01_metadata.pkl')
# metadata = pd.read_pickle('h01_metadata_c3.pkl')
# c3_cloudvolume = cloudvolume.CloudVolume('gs://h01-release/data/20210601/c3', progress=True)

data = json.load(open('metadata.json','r'))

# put the metadata into a DataFrame
mydata = {'ids':data['inline']['ids']}
for i,tag in enumerate(data['inline']['properties'][0]['tags']):
  mydata[tag] = [i in tags for tags in data['inline']['properties'][0]['values']]
for i in range(1,len(data['inline']['properties'])):
  mydata[data['inline']['properties'][i]['description']] = data['inline']['properties'][i]['values']
metadata = pd.DataFrame.from_dict(mydata)
metadata = metadata.set_index('ids')

soma_data = pd.read_csv('somas.csv')

layers = ['L1',
          'L2',
          'L3',
          'L4',
          'L5',
          'L6',
          'layer-unclassified']
cells = ['pyramidal', 'interneuron', 'spiny-stellate', 'astrocyte', 'blood-vessel-cell']
metrics = ['nCell', 'Volume', 'avgVolume', 'stdVolume', 'avgNinExc', 'stdNinExc', 'avgNinInh', 'stdNinInh', 
        'avgNout', 'stdNout', 'cell_locs', 'cell_ids']
vol_str = 'Volume (8x8x33nm voxels)'

Vtissue = 1000 ** 3

missing_somas = open('missing_somas.txt', 'w')

data = {}
not_in_soma_data = []
somewhere = []
for cell in cells:
    data[cell] = {}
    print(cell)
    for layer in layers:
        data[cell][layer] = {}
        print(layer)
        data[cell][layer]['nCell'] = len(metadata[metadata[cell] & metadata[layer]])
        print(metrics[0] + ': ' + str(data[cell][layer][metrics[0]]))
        data[cell][layer]['Volume'] = np.sum(metadata[metadata[cell] & metadata[layer]][vol_str]) * 2.11200e-6
        print(metrics[1] + ': ' + str(data[cell][layer][metrics[1]]))
        if data[cell][layer]['nCell'] > 0:
            data[cell][layer]['avgVolume'] = np.mean(data[cell][layer][metrics[1]]) / data[cell][layer][metrics[0]]
            data[cell][layer]['stdVolume'] = np.std(metadata[metadata[cell] & metadata[layer]][vol_str]) * 2.11200e-6
        else:
            data[cell][layer]['avgVolume'] = 0.0
        print(metrics[2] + ': ' + str(data[cell][layer][metrics[2]]))
        data[cell][layer]['avgNinExc'] = np.mean(metadata[metadata[cell] & metadata[layer]]['Number of incoming excitatory synapses'])
        print('Average number of incoming excitatory syns' + ':' + str(data[cell][layer][metrics[4]]))
        data[cell][layer]['stdNinExc'] = np.std(metadata[metadata[cell] & metadata[layer]]['Number of incoming excitatory synapses'])
        print('Std of number of incoming excitatory syns: ' + str(data[cell][layer][metrics[5]]))
        data[cell][layer]['avgNinInh'] = np.mean(metadata[metadata[cell] & metadata[layer]]['Number of incoming inhibitory synapses'])
        print('Average number of incoming excitatory syns' + ':' + str(data[cell][layer][metrics[6]]))
        data[cell][layer]['stdNinInh'] = np.std(metadata[metadata[cell] & metadata[layer]]['Number of incoming inhibitory synapses'])
        print('Std of number of incoming excitatory syns: ' + str(data[cell][layer][metrics[7]]))
        data[cell][layer]['avgNout'] = np.mean(metadata[metadata[cell] & metadata[layer]]['Number of outgoing synapses'])
        print('Average number of outgoing syns' + ':' + str(data[cell][layer][metrics[8]]))
        data[cell][layer]['stdNout'] = np.std(metadata[metadata[cell] & metadata[layer]]['Number of outgoing synapses'])
        print('Std of number of outgoing syns: ' + str(data[cell][layer][metrics[9]]))
        data[cell][layer]['cell_locs'] = []
        data[cell][layer]['cell_ids'] = []
        if data[cell][layer]['nCell'] > 0:
            for celli in metadata[metadata[cell] & metadata[layer]].iloc:
                try:
                    soma = soma_data[soma_data['c3_rep_strict'] == int(celli.name)]
                    x = int(soma.x.values)
                    y=  int(soma.y.values)
                    z = int(soma.z.values)
                    data[cell][layer]['cell_locs'].append([x,y,z])
                    data[cell][layer]['cell_ids'].append(celli.name)
                    somewhere.append(celli.name)
                    if cell.upper().replace('-','_') != soma['celltype']:
                        print('Cell ID: %s has cell type conflict' % (celli.name))
                    # skel = c3_cloudvolume.skeleton.get(int(celli.name))
                    # soma_ind = np.argmax(skel.radii)
                    # data[cell][layer]['cell_locs'].append(list(skel.vertices[soma_ind]))
                except:
                    try:
                        soma = soma_data[soma_data['c3_rep_manual'] == int(celli.name)]
                        x = int(soma.x.values)
                        y=  int(soma.y.values)
                        z = int(soma.z.values)
                        data[cell][layer]['cell_locs'].append([x,y,z])
                        data[cell][layer]['cell_ids'].append(celli.name)
                        somewhere.append(celli.name)
                        if cell.upper().replace('-','_') != soma['celltype']:
                            print('Cell ID: %s has cell type conflict' % (celli.name))
                    except:
                        try:
                            soma = soma_data[soma_data['c2_rep_strict'] == int(celli.name)]
                            x = int(soma.x.values)
                            y=  int(soma.y.values)
                            z = int(soma.z.values)
                            data[cell][layer]['cell_locs'].append([x,y,z])
                            data[cell][layer]['cell_ids'].append(celli.name)
                            somewhere.append(celli.name)
                            if cell.upper().replace('-','_') != soma['celltype']:
                                print('Cell ID: %s has cell type conflict' % (celli.name))
                        except:
                            try:
                                soma = soma_data[soma_data['c2_rep_manual'] == int(celli.name)]
                                x = int(soma.x.values)
                                y=  int(soma.y.values)
                                z = int(soma.z.values)
                                data[cell][layer]['cell_locs'].append([x,y,z])
                                data[cell][layer]['cell_ids'].append(celli.name)
                                somewhere.append(celli.name)
                                if cell.upper().replace('-','_') != soma['celltype']:
                                    print('Cell ID: %s has cell type conflict' % (celli.name))
                            except:
                                missing_somas.write('Cell ID %s is missing somas.csv\n' % (celli.name))
                                not_in_soma_data.append(celli.name)

    print('\n')

missing_somas.close()

print('%i cells from metadata.json found in somas.csv' % (len(somewhere)))
print('%s cells from metadata.json not found in somas.csv\n' % (len(not_in_soma_data)))

# compute neuronal volume fraction 
Vol_nrn = 0
for cell in cells[:3]:
    for layer in layers:
        Vol_nrn = Vol_nrn + data[cell][layer]['Volume']

beta_nrn = Vol_nrn / Vtissue
print('beta_nrn: ' + str(beta_nrn))

# plotting a subset of pyramidal cells 
# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')
# cell = 'pyramidal'
# for layer, color in zip(layers[1:-2], ['b','r','g','k']):
#     for i in range(30):
#         loc = data[cell][layer]['cell_locs'][i]
#         ax.scatter(loc[0], loc[1], loc[2], color=color)
# plt.ion()
# plt.show()

def findConns(input_data):
    cell_id = input_data[0]
    conn_file = input_data[1]
    return_list = input_data[2]
    reader = DataFileReader(open('./exported/'+conn_file, "rb"), 
                DatumReader())
    conns = []
    for conn in reader:
        if str(conn['pre_synaptic_site']['neuron_id']) == cell_id:
            print('%s: found as presynaptic neuron' % (cell_id))
            return_list.append(conn)
        elif conn['pre_synaptic_site']['base_neuron_id'] == cell_id:
            print('%s: presynaptic base neuron' % (cell_id))
            return_list.append(conn)
        elif str(conn['post_synaptic_partner']['neuron_id']) == cell_id:
            print('%s: postsynaptic neuron' % (cell_id))
            return_list.append(conn)
    

# look for synapse involving example cell
manager = multiprocessing.Manager()
conns = manager.list()

# inds = [i for i in range(10)]
inds = [0]
layer = 'L4'
conn_files = listdir('./exported/')

input_data = []
for ind in inds:
    for conn_file in conn_files:
        if len(conn_file.split('.')) == 1:
            cell_id = data[cell][layer]['cell_ids'][ind]
            input_data.append([cell_id, conn_file, conns])

input_data = tuple(input_data)
p = multiprocessing.Pool(40)
p.map(findConns, input_data)

# for ind in inds:
#     cell_id = data[cell][layer]['cell_ids'][ind]
#     conn_files = listdir('./exported/')
#     conns = []
#     for conn_file in conn_files[:1]:
#         if len(conn_file.split('.')) == 1:
#             reader = DataFileReader(open('./exported/'+conn_file, "rb"), 
#                 DatumReader())
#             for conn in reader:
#                 if str(conn['pre_synaptic_site']['neuron_id']) == cell_id:
#                     print('%s: found as presynaptic neuron' % (cell_id))
#                     conns.append(conn)
#                 elif conn['pre_synaptic_site']['base_neuron_id'] == cell_id:
#                     print('%s: presynaptic base neuron' % (cell_id))
#                     conns.append(conn)
#                 elif str(conn['post_synaptic_partner']['neuron_id']) == cell_id:
#                     print('%s: postsynaptic neuron' % (cell_id))
#                     conns.append(conn)