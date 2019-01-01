#!/usr/bin/env python3

import socket
import struct
import sys
from datetime import datetime,timedelta
from bts_order import BTS_Order

_omsBuyOrderList = []
_omsSellOrderList = []

def addToOrderList(_orderList, _newRcvdOrder):
    if not isinstance(_newRcvdOrder, BTS_Order):
        print('Something is wrong. Check.')
        sys.exit()
    else:
        _listLen = len(_orderList)
        _listIndex = 0
        while _listIndex < _listLen:
            if _newRcvdOrder._orderPosition == 'buy':
                if (_orderList[_listIndex]._stdOrderType == 'market' and _newRcvdOrder._stdOrderType == 'limit'):
                    _listIndex = _listIndex + 1
                elif (_orderList[_listIndex]._stdOrderType == 'limit' and _newRcvdOrder._stdOrderType == 'market'):
                    print('Order added at index {0}.'.format(_listIndex))
                    _orderList.insert(_listIndex, _newRcvdOrder)
                    break
                else:
                    if ((str(_orderList[_listIndex]._limitPrice) == str(_newRcvdOrder._limitPrice)) or
                        (_orderList[_listIndex]._stdOrderType == 'market' and _newRcvdOrder._stdOrderType == 'market')):
                        print('Checking prioritization based on timestamp...')
                        _timeDifference = _newRcvdOrder._orderDateTime - _orderList[_listIndex]._orderDateTime
                        #print('TD:{0}days, {1}seconds and {2}microseconds'.format(_timeDifference.days, _timeDifference.seconds, _timeDifference.microseconds))
                        if _timeDifference.days < 0:
                            print('Order added at index {0}.'.format(_listIndex))
                            _orderList.insert(_listIndex, _newRcvdOrder)
                            break
                        else:
                            if (_timeDifference.days == 0 and _timeDifference.seconds == 0 and _timeDifference.microseconds == 0):
                                print('Checking prioritization based on fulfilment type...')
                                if (_orderList[_listIndex]._fulfilmentType == 'partial' and _newRcvdOrder._fulfilmentType == 'all-or-nothing'):
                                    print('Order added at index {0}.'.format(_listIndex))
                                    _orderList.insert(_listIndex, _newRcvdOrder)
                                    break
                                elif (_orderList[_listIndex]._fulfilmentType == 'all-or-nothing' and _newRcvdOrder._fulfilmentType == 'partial'):
                                    _listIndex = _listIndex + 1
                                else:
                                    print('Checking prioritization based on order quantity...')
                                    if (_orderList[_listIndex]._orderQty < _newRcvdOrder._orderQty):
                                        print('Order added at index {0}.'.format(_listIndex))
                                        _orderList.insert(_listIndex, _newRcvdOrder)
                                        break
                                    elif (_orderList[_listIndex]._orderQty > _newRcvdOrder._orderQty):
                                        _listIndex = _listIndex + 1
                                    else:
                                        print('Remaining: Customer Type -> Coin Toss')
                                        print('Order added at index {0}.'.format(_listIndex+1))
                                        if (_listIndex + 1) < _listLen:
                                            _orderList.insert(_listIndex+1, _newRcvdOrder)
                                        else:
                                            _orderList.append(_newRcvdOrder)
                                        break
                            else:
                                _listIndex = _listIndex + 1
                    else:
                        if _orderList[_listIndex]._limitPrice > _newRcvdOrder._limitPrice:
                            _listIndex = _listIndex + 1
                        else:
                            print('Order added at index {0}.'.format(_listIndex))
                            _orderList.insert(_listIndex, _newRcvdOrder)
                            break
            else:
                if (_orderList[_listIndex]._stdOrderType == 'market' and _newRcvdOrder._stdOrderType == 'limit'):
                    _listIndex = _listIndex + 1
                elif (_orderList[_listIndex]._stdOrderType == 'limit' and _newRcvdOrder._stdOrderType == 'market'):
                    print('Order added at index {0}.'.format(_listIndex))
                    _orderList.insert(_listIndex, _newRcvdOrder)
                    break
                else:
                    if ((str(_orderList[_listIndex]._limitPrice) == str(_newRcvdOrder._limitPrice)) or
                        (_orderList[_listIndex]._stdOrderType == 'market' and _newRcvdOrder._stdOrderType == 'market')):
                        print('Checking prioritization based on timestamp...')
                        _timeDifference = _newRcvdOrder._orderDateTime - _orderList[_listIndex]._orderDateTime
                        #print('TD:{0}days, {1}seconds and {2}microseconds'.format(_timeDifference.days, _timeDifference.seconds, _timeDifference.microseconds))
                        if _timeDifference.days < 0:
                            print('Order added at index {0}.'.format(_listIndex))
                            _orderList.insert(_listIndex, _newRcvdOrder)
                            break
                        else:
                            if (_timeDifference.days == 0 and _timeDifference.seconds == 0 and _timeDifference.microseconds == 0):
                                print('Checking prioritization based on fulfilment type...')
                                if (_orderList[_listIndex]._fulfilmentType == 'partial' and _newRcvdOrder._fulfilmentType == 'all-or-nothing'):
                                    print('Order added at index {0}.'.format(_listIndex))
                                    _orderList.insert(_listIndex, _newRcvdOrder)
                                    break
                                elif (_orderList[_listIndex]._fulfilmentType == 'all-or-nothing' and _newRcvdOrder._fulfilmentType == 'partial'):
                                    _listIndex = _listIndex + 1
                                else:
                                    print('Checking prioritization based on order quantity...')
                                    if (_orderList[_listIndex]._orderQty < _newRcvdOrder._orderQty):
                                        print('Order added at index {0}.'.format(_listIndex))
                                        _orderList.insert(_listIndex, _newRcvdOrder)
                                        break
                                    elif (_orderList[_listIndex]._orderQty > _newRcvdOrder._orderQty):
                                        _listIndex = _listIndex + 1
                                    else:
                                        print('Remaining: Customer Type -> Coin Toss')
                                        print('Order added at index {0}.'.format(_listIndex+1))
                                        if (_listIndex + 1) < _listLen:
                                            _orderList.insert(_listIndex+1, _newRcvdOrder)
                                        else:
                                            _orderList.append(_newRcvdOrder)
                                        break
                            else:
                                _listIndex = _listIndex + 1
                    else:
                        if _orderList[_listIndex]._limitPrice < _newRcvdOrder._limitPrice:
                            _listIndex = _listIndex + 1
                        else:
                            print('Order added at index {0}.'.format(_listIndex))
                            _orderList.insert(_listIndex, _newRcvdOrder)
                            break
        if _listIndex == _listLen: 
            _orderList.append(_newRcvdOrder)
            print('Order added at index {0}.'.format(_listIndex))

def printUpdatedOrderQueue(_orderList):
    _parseIndex = 0
    while _parseIndex < len(_orderList):
        print('\nParticipant Id:{0} Quantity:{1} OrderType: {2} {3} LimitPrice:{4}'.format(_orderList[_parseIndex]._participantId, _orderList[_parseIndex]._orderQty, _orderList[_parseIndex]._fulfilmentType,
                                                                                              _orderList[_parseIndex]._stdOrderType, _orderList[_parseIndex]._limitPrice))
        _parseIndex = _parseIndex + 1
            
def updateOrderQueue(_orderList, _mIndices):
    _orderType = _orderList[0]._orderPosition
    _ordersRemoved = 0
    for _indices in _mIndices:
        if _orderList[_indices - _ordersRemoved]._orderQty == 0:
            del _orderList[_indices - _ordersRemoved]
            _ordersRemoved = _ordersRemoved + 1
    if len(_orderList) > 0:
        print('\nOutstanding {0} orders: {1}'.format(_orderType, len(_orderList)))
        printUpdatedOrderQueue(_orderList)
    else:
        print('\n{0} order list is empty.'.format(_orderType))
        
                        
def start_oms_server():
    _oms_socket = socket.socket()
    _oms_port = 6667
    _oms_socket.bind(('', _oms_port))
    print('Socket binded to %s' %(_oms_port))
    _oms_socket.listen(10)
    print('Socket is listening')

    while True:
        #Loop Initialization
        _oms_client, _oms_cli_addr = _oms_socket.accept()
        print('\nNew Order')
        _participantId = 0
        _orderType = 8
        _orderQuantity = 0
        _limitPrice = 0
        _minPartialFillQty = 0
        _orderYear = 0
        _orderMonth = 0
        _orderDay = 0
        _orderHour = 0
        _orderMinute = 0
        _orderSecond = 0
        _orderMicroSecond = 0
        
        _newOrder = None
        _matchedIndices = None
        
        #Receive Order Parameters
        _pId = _oms_client.recv(4)
        _otype = _oms_client.recv(4)
        _oqty = _oms_client.recv(4)
        _limPrice = _oms_client.recv(4)
        _minParFillQty = _oms_client.recv(4)
        _oYear = _oms_client.recv(4)
        _oMonth = _oms_client.recv(4)
        _oDay = _oms_client.recv(4)
        _oHour = _oms_client.recv(4)
        _oMinute = _oms_client.recv(4)
        _oSecond = _oms_client.recv(4)
        _oMicroSecond = _oms_client.recv(4)
        
        #Unpacking received data into correct structures
        _participantId = struct.unpack('i', _pId)[0]
        _orderType = struct.unpack('i', _otype)[0]
        _orderQuantity = struct.unpack('i', _oqty)[0]
        if (_orderType % 2 == 1):
            _limitPrice = struct.unpack('f', _limPrice)[0]
        _minPartialFillQty = struct.unpack('i', _minParFillQty)[0]
        _orderYear = struct.unpack('i', _oYear)[0]
        _orderMonth = struct.unpack('i', _oMonth)[0]
        _orderDay = struct.unpack('i', _oDay)[0]
        _orderHour = struct.unpack('i', _oHour)[0]
        _orderMinute = struct.unpack('i', _oMinute)[0]
        _orderSecond = struct.unpack('i', _oSecond)[0]
        _orderMicroSecond = struct.unpack('i', _oMicroSecond)[0]

        _orderDateTime = datetime(_orderYear, _orderMonth, _orderDay, _orderHour, _orderMinute, _orderSecond, _orderMicroSecond, None)
        print(_orderDateTime)

        _newOrder = BTS_Order(_participantId, _orderType, _orderQuantity, _limitPrice, _minPartialFillQty, _orderDateTime)

        if _newOrder._orderPosition == 'buy':
            _buyOrderListLen = len(_omsBuyOrderList)
            if not _omsSellOrderList:
                print('Adding to {0} order queue...'.format(_newOrder._orderPosition))
                if not _omsBuyOrderList:
                    _omsBuyOrderList.append(_newOrder)
                else:
                    addToOrderList(_omsBuyOrderList, _newOrder)
                printUpdatedOrderQueue(_omsBuyOrderList)
            else:
                _matchedIndices = _newOrder.check_for_match(_omsSellOrderList)
                if _matchedIndices is None:
                    if not _omsBuyOrderList:
                        _omsBuyOrderList.append(_newOrder)
                    else:
                        addToOrderList(_omsBuyOrderList, _newOrder)
                    printUpdatedOrderQueue(_omsBuyOrderList)
                else:
                    print(_matchedIndices)
                    updateOrderQueue(_omsSellOrderList, _matchedIndices)
                    if _newOrder._orderQty != 0:
                        addToOrderList(_omsBuyOrderList, _newOrder)
                        printUpdatedOrderQueue(_omsBuyOrderList)

        else:
            _sellOrderListLen = len(_omsSellOrderList)
            if not _omsBuyOrderList:
                print('Adding to {0} order queue...'.format(_newOrder._orderPosition))
                if not _omsSellOrderList:
                    _omsSellOrderList.append(_newOrder)
                else:
                    addToOrderList(_omsSellOrderList, _newOrder)
                printUpdatedOrderQueue(_omsSellOrderList)
            else:
                _matchedIndices = _newOrder.check_for_match(_omsBuyOrderList)
                if _matchedIndices is None:
                    if not _omsSellOrderList:
                        _omsSellOrderList.append(_newOrder)
                    else:
                        addToOrderList(_omsSellOrderList, _newOrder)
                    printUpdatedOrderQueue(_omsSellOrderList)
                else:
                    print(_matchedIndices)
                    updateOrderQueue(_omsBuyOrderList, _matchedIndices)
                    if _newOrder._orderQty != 0:
                        addToOrderList(_omsSellOrderList, _newOrder)
                        printUpdatedOrderQueue(_omsSellOrderList)
                    
start_oms_server()
