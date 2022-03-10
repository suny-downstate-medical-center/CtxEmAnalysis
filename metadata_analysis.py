import cloudvolume
import json
import pandas as pd
import numpy as np 

# metadata = pd.read_pickle('h01_metadata.pkl')
# metadata = pd.read_pickle('h01_metadata_c3.pkl')
c3_cloudvolume = cloudvolume.CloudVolume('gs://h01-release/data/20210601/c3', progress=True)

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

layers = ['L1',
          'L2',
          'L3',
          'L4',
          'L5',
          'L6',
          'layer-unclassified']
cells = ['pyramidal', 'interneuron', 'spiny-stellate', 'astrocyte', 'blood-vessel-cell']
metrics = ['nCell', 'Volume', 'avgVolume', 'stdVolume', 'avgNinExc', 'stdNinExc', 'avgNinInh', 'stdNinInh', 
        'avgNout', 'stdNout', 'cell_locs']
vol_str = 'Volume (8x8x33nm voxels)'

Vtissue = 1000 ** 3

data = {}
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
        if data[cell][layer]['nCell'] > 0:
            for celli in metadata[metadata[cell] & metadata[layer]].iloc:
                skel = c3_cloudvolume.skeleton.get(int(celli.name))
                soma_ind = np.argmax(skel.radii)
                data[cell][layer]['cell_locs'].append(list(skel.vertices[soma_ind]))
    print('\n')

# Vol_nrn = 0
# for cell in cells[:3]:
#     for layer in layers:
#         Vol_nrn = Vol_nrn + data[cell][layer]['Volume']

# beta_nrn = Vol_nrn / Vtissue
# print('beta_nrn: ' + str(beta_nrn))