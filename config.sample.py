from os import path
DATA_DIR = path.join(path.realpath(path.curdir), "data")
TOKYO_SERVER_PARMS = '#bnum=1000000#fpow=13#opts=ldf'

USE_MASTER = True
DEBUG = False

NODES = {
    #Lookup nodes
    'lookup1_A': { 'id': 1, 'host': '127.0.0.1:41201', 'master': '127.0.0.1:51201' },
    'lookup1_B': { 'id': 2, 'host': '127.0.0.1:51201', 'master': '127.0.0.1:41201' },

    #Storage nodes
    'storage1_A': { 'id': 5, 'host': '127.0.0.1:44201', 'master': '127.0.0.1:54201' },
    'storage1_B': { 'id': 6, 'host': '127.0.0.1:54201', 'master': '127.0.0.1:44201' },
}
