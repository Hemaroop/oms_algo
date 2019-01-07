#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime
import bts_constraints

def print_order_help():
    print('python3 oms_client_quote_static_timestamp.py -i participant_id --bPrice [bid price] --bSize [bid size] --aPrice [ask price] --aSize [ask size] -gt number of days')
    print('Participant id: [101, 110]')
    print('Order quantity: Must be greater than minimum order size.')
    print('Number of days: [0, 14]')
    
def send_order_to_server():
    #Order parametric initialization
    _participant_id = 0
    _bid_price = 0
    _bid_size = 0
    _ask_price = 0
    _ask_size = 0
    _minimum_order_size = bts_constraints._btsMinOrderSize
    _min_order_size_increment = bts_constraints._btsMinOrderIncrement
    _min_partial_fill_qty = 0
    _time_in_force = 14
    _order_date_time = datetime.now()

    #Required Boolean Flags
    _pidFound = False
    _bPriceFound = False
    _bSizeFound = False
    _aPriceFound = False
    _aSizeFound = False
    
    #TCP port specifications
    _oms_port = 6666
    _oms_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    argv = sys.argv[1:]

    _parseIndex = 0

    while _parseIndex < len(argv):
        if argv[_parseIndex] == '-h':
            print_order_help()
            sys.exit()
        elif argv[_parseIndex] == '-i':
            try:
                _parseIndex = _parseIndex + 1
                _participant_id = int(argv[_parseIndex])
                if ((_participant_id > 100) and (_participant_id <= 110)):
                    _pidFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '--bPrice':
            try:
                _parseIndex = _parseIndex + 1
                _bid_price = float(argv[_parseIndex])
                _bPriceFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '--aPrice':
            try:
                _parseIndex = _parseIndex + 1
                _ask_price = float(argv[_parseIndex])
                _aPriceFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '--bSize':
            try:
                _parseIndex = _parseIndex + 1
                _bid_size = int(argv[_parseIndex])
                _bSizeFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '--aSize':
            try:
                _parseIndex = _parseIndex + 1
                _ask_size = int(argv[_parseIndex])
                _aSizeFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '-gt':
            try:
                _parseIndex = _parseIndex + 1
                _time_in_force = int(argv[_parseIndex])
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        else:
            print('Unknown argument. Exiting...')
            sys.exit()
        _parseIndex = _parseIndex + 1

    if _pidFound and _bPriceFound and _aPriceFound and _bSizeFound and _aSizeFound:
        n = int((_bid_size - _minimum_order_size) / _min_order_size_increment)
        if (_minimum_order_size + (n+1)*_min_order_size_increment - _bid_size) < _min_order_size_increment:
            print('ERROR: Quantity is not as per requirements.')
            sys.exit()
        n = int((_ask_size - _minimum_order_size) / _min_order_size_increment)
        if (_minimum_order_size + (n+1)*_min_order_size_increment - _ask_size) < _min_order_size_increment:
            print('ERROR: Quantity is not as per requirements.')
            sys.exit()
        _min_partial_fill_qty = _min_order_size_increment

        try:
            #Initialize socket
            _oms_socket.connect(('127.0.0.1', _oms_port))
            print('Socket successfully connected to OMS server.')
            
            #Sending Order to OMS server
            _participantId = bytearray(struct.pack('i', _participant_id))
            _bidPrice = bytearray(struct.pack('f', _bid_price))
            _bidSize = bytearray(struct.pack('i', _bid_size))
            _askPrice = bytearray(struct.pack('f', _ask_price))
            _askSize = bytearray(struct.pack('i', _ask_size))
            _minParFillQty = bytearray(struct.pack('i', _min_partial_fill_qty))
            _timeInForce = bytearray(struct.pack('i', _time_in_force))
            _orderYear = bytearray(struct.pack('i', int(_order_date_time.year)))
            _orderMonth = bytearray(struct.pack('i', int(_order_date_time.month)))
            _orderDay = bytearray(struct.pack('i', int(_order_date_time.day)))
            _orderHour = bytearray(struct.pack('i', 0))
            _orderMinutes = bytearray(struct.pack('i', 0))
            _orderSeconds = bytearray(struct.pack('i', 0))
            _orderMicroSeconds = bytearray(struct.pack('i', 0))
                
            print(_participantId)
            print(_bidPrice)
            print(_bidSize)
            print(_askPrice)
            print(_askSize)
            print(_minParFillQty)
            print(_timeInForce)
            print(_orderYear)
            print(_orderMonth)
            print(_orderDay)
            print(_orderHour)
            print(_orderMinutes)
            print(_orderSeconds)
            print(_orderMicroSeconds)

            _oms_socket.send(_participantId)
            _oms_socket.send(_bidPrice)
            _oms_socket.send(_bidSize)
            _oms_socket.send(_askPrice)
            _oms_socket.send(_askSize)
            _oms_socket.send(_minParFillQty)
            _oms_socket.send(_timeInForce)
            _oms_socket.send(_orderYear)
            _oms_socket.send(_orderMonth)
            _oms_socket.send(_orderDay)
            _oms_socket.send(_orderHour)
            _oms_socket.send(_orderMinutes)
            _oms_socket.send(_orderSeconds)
            _oms_socket.send(_orderMicroSeconds)
                
            _oms_socket.close()
        except socket.error as err:
            print('Error: %s' %(err))
            sys.exit()

    else:
        print('Invalid order submitted.')
        print_order_help()

send_order_to_server()

