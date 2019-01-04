#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime
import bts_constraints

def print_order_help():
    print('python3 oms_client.py -i participant_id -t order_type -q order_qty -gt number of days -l limit_price (used only if order_type is 1 or 3)')
    print('Participant id: [1,100]')
    print('Order type: [0,8). Refer to readme for information on order type codes.')
    print('Order quantity: Must be greater than minimum order size.')
    print('Number of days: [0, 14]')
    
def send_order_to_server():
    #Order parametric initialization
    _participant_id = 0
    _order_type = 8
    _order_qty = 0
    _minimum_order_size = bts_constraints._btsMinOrderSize
    _min_order_size_increment = bts_constraints._btsMinOrderIncrement
    _min_partial_fill_qty = 0
    _time_in_force = 14
    _limit_price = 0
    _order_date_time = datetime.now()

    #Required Boolean Flags
    _pidFound = False
    _oTypeFound = False
    _oQtyFound = False
    _oLPFound = False
    
    #TCP port specifications
    _oms_port = 6667
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
                _pidFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '-t':
            try:
                _parseIndex = _parseIndex + 1
                _order_type = int(argv[_parseIndex])
                _oTypeFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '-q':
            try:
                _parseIndex = _parseIndex + 1
                _order_qty = int(argv[_parseIndex])
                _oQtyFound = True
            except ValueError as err:
                print('ERROR: %s' %err)
                sys.exit()
        elif argv[_parseIndex] == '-l':
            try:
                _parseIndex = _parseIndex + 1
                _limit_price = float(argv[_parseIndex])
                _oLPFound = True
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

    if _pidFound and _oTypeFound and _oQtyFound:
        n = int((_order_qty - _minimum_order_size) / _min_order_size_increment)
        if (_minimum_order_size + (n+1)*_min_order_size_increment - _order_qty) < _min_order_size_increment:
            print('ERROR: Quantity is not as per requirements.')
            sys.exit()
        if ((_order_type % 2) == 1):
            if not _oLPFound:
                print('Price missing for limit order')
                sys.exit()
        if _order_type < 4:
            print('Buy order quantity: %d' %_order_qty)
            if ((_order_type % 2) == 1):
                print('Limit Order. Limit price: %f' %_limit_price)
            else:
                print('Market Order. Ignoring limit price...')
        else:
            print('Sell order quantity: %d' %_order_qty)
            if ((_order_type % 2) == 1):
                print('Limit price: %f' %_limit_price)
            else:
                print('Ignoring limit price...')
        if (int(_order_type / 2) % 2) == 1:
            print('All-or-nothing')
            _min_partial_fill_qty = _order_qty
        else:
            print('Partial-fill')
            _min_partial_fill_qty = _min_order_size_increment

        try:
            #Initialize socket
            _oms_socket.connect(('127.0.0.1', _oms_port))
            print('Socket successfully connected to OMS server.')
            
            #Sending Order to OMS server
            _participantId = bytearray(struct.pack('i', _participant_id))
            _orderType = bytearray(struct.pack('i', _order_type))
            _orderQty = bytearray(struct.pack('i', _order_qty))
            _limitPrice = bytearray(struct.pack('f', _limit_price))
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
            print(_orderType)
            print(_orderQty)
            print(_limitPrice)
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
            _oms_socket.send(_orderType)
            _oms_socket.send(_orderQty)
            _oms_socket.send(_limitPrice)
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

