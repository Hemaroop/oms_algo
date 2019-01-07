#!/usr/bin/env python3

import sys
import random
from datetime import datetime
import bts_constraints

def printUsage():
    print('Help: python3 generate_client_script.py -h')
    print('For n orders: python3 generate_client_script.py n')

_scriptCreationTime = datetime.now()
_scriptFileNameSuffix = '{0}{1}{2}{3}{4}{5}{6}'.format(_scriptCreationTime.year, _scriptCreationTime.month, _scriptCreationTime.day, _scriptCreationTime.hour, _scriptCreationTime.minute, _scriptCreationTime.second, _scriptCreationTime.microsecond)
_scriptFileName = '_autoOrderScript{0}.sh'.format(_scriptFileNameSuffix)

_pythonEnv = 'python3'
omsClientCommands = ['oms_client_order.py', 'oms_client_order_static_timestamp.py']
_numOrders = 500

argv = sys.argv[1:]

if len(argv) == 1:
    if argv[0] == '-h':
        printUsage()
    else:
        try:
            _numOrders = int(argv[0])
        except ValueError as err:
            print('ERROR: %s' %err)
            printUsage()
            sys.exit()
else:
    if not argv is None:
        printUsage()
    sys.exit()
    
_scriptFile = open(_scriptFileName, 'w')
_scriptFile.write('#!/bin/sh\n')

for _orderIndex in range(_numOrders):
    _orderCommand = ''
    _clientCommandIndex = random.randint(0,1)
    _participantId = random.randint(1,100)
    _orderType = random.randint(0,7)
    _qtyMultiplier = random.randint(0,bts_constraints._btsMaxMultiplier-1)
    _orderQty = bts_constraints._btsMinOrderSize + (_qtyMultiplier * bts_constraints._btsMinOrderIncrement)
    _limitPrice = random.uniform(95.0, 105.0)
    _timeInForce = random.randint(0, 14)
    _sleepTime = random.uniform(0.0, 3.0)

    if (_orderType % 2) == 1:
        _orderCommand = '{0} {1} -i {2} -t {3} -q {4} -l {5} -gt {6}\n'.format(_pythonEnv, omsClientCommands[_clientCommandIndex], _participantId, _orderType, _orderQty, _limitPrice, _timeInForce)
    else:
        _orderCommand = '{0} {1} -i {2} -t {3} -q {4} -gt {5}\n'.format(_pythonEnv, omsClientCommands[_clientCommandIndex], _participantId, _orderType, _orderQty, _timeInForce)
        
    if _orderIndex == 0:
        _scriptFile.write(_orderCommand)
    else:
        _scriptFile.write('\nif [ $? -eq 0 ]; then\n')
        _scriptFile.write('\tsleep {0}\n'.format(_sleepTime))
        _scriptFile.write('\t{0}'.format(_orderCommand))
        _scriptFile.write('fi\n')
        
_scriptFile.close()
