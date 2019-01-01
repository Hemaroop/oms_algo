#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime
import bts_constraints

def print_order_help():
    print('python3 oms_client.py participant_id order_type order_qty limit_price (used only if order_type is 1 or 3)')
    print('Participant id: [1,100]')
    print('Order type: [0,8). Refer to readme for information on order type codes.')
    print('Order quantity: Must be greater than minimum order size.')

def send_order_to_server():
    #Order parametric initialization
    _participant_id = 0
    _order_type = 8
    _order_qty = 0
    _minimum_order_size = bts_constraints._btsMinOrderSize
    _min_order_size_increment = bts_constraints._btsMinOrderIncrement
    _min_partial_fill_qty = 0
    _limit_price = 0
    _order_date_time = datetime.utcnow()
    
    #TCP port specifications
    _oms_port = 6667
    _oms_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    argv = sys.argv[1:]

    try:
        if argv[0] == '-h':
            print_order_help()

        elif (int(argv[0]) <= 100) and (int(argv[0]) > 0) and (int(argv[1]) < 8) and (len(argv) >= 3):
            _participant_id = int(argv[0])
            _order_type = int(argv[1])
            _order_qty = int(argv[2])
            n = int((_order_qty - _minimum_order_size) / _min_order_size_increment)
            if (_minimum_order_size + (n+1)*_min_order_size_increment - _order_qty) < _min_order_size_increment:
                print('ERROR: Quantity is not as per requirements.')
                sys.exit()
            if ((_order_type % 2) == 1):
                if len(argv) < 4:
                    print('Argument missing for limit order')
                    sys.exit()
                _limit_price = float(argv[3])                
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
                _orderYear = bytearray(struct.pack('i', int(_order_date_time.year)))
                _orderMonth = bytearray(struct.pack('i', int(_order_date_time.month)))
                _orderDay = bytearray(struct.pack('i', int(_order_date_time.day)))
                _orderHour = bytearray(struct.pack('i', int(_order_date_time.hour)))
                _orderMinutes = bytearray(struct.pack('i', int(_order_date_time.minute)))
                _orderSeconds = bytearray(struct.pack('i', int(_order_date_time.second)))
                _orderMicroSeconds = bytearray(struct.pack('i', int(_order_date_time.microsecond)))
                
                print(_participantId)
                print(_orderType)
                print(_orderQty)
                print(_limitPrice)
                print(_minParFillQty)
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
    except ValueError as err:
        print('ERROR: %s' %err)
        
send_order_to_server()

