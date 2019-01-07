#!/usr/bin/env python3

import socket
import struct
import sys
import time
import datetime
import btsTradingHours
from sched import scheduler
from threading import Thread, Lock
from bts_order import BTS_Order
from bts_quote import BTS_Quote

_omsBuyOrderList = []
_omsSellOrderList = []

_tradingDayOpeningTime = datetime.time(btsTradingHours._btsOpeningHour, btsTradingHours._btsOpeningMinute,
                                              btsTradingHours._btsOpeningSecond, btsTradingHours._btsOpeningMicrosecond)
_tradingDayClosingTime = datetime.time(btsTradingHours._btsClosingHour, btsTradingHours._btsClosingMinute,
                                              btsTradingHours._btsClosingSecond, btsTradingHours._btsClosingMicrosecond)
_scheduleTradingDayStartHandler = False
_scheduleTradingDayCloseHandler = False

_orderQueueAccessLock = Lock()

def printUpdatedOrderQueue(_orderList):
    _parseIndex = 0
    while _parseIndex < len(_orderList):
        print('\nParticipant Id:{0} Quantity:{1} OrderType: {2} {3} LimitPrice:{4}'.format(_orderList[_parseIndex]._participantId, _orderList[_parseIndex]._orderQty, _orderList[_parseIndex]._fulfilmentType,
                                                                                              _orderList[_parseIndex]._stdOrderType, _orderList[_parseIndex]._limitPrice))
        _parseIndex = _parseIndex + 1
            
def updateOrderQueue(_orderList, _mIndices):
    _orderQueueAccessLock.acquire()
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
    _orderQueueAccessLock.release()

def _tradingDayStartHandler():
    _orderQueueAccessLock.acquire()
    
    global _omsBuyOrderList
    global _omsSellOrderList
    global _scheduleTradingDayStartHandler
    global _scheduleTradingDayCloseHandler
    
    _scheduleTradingDayStartHandler = False
    _scheduleTradingDayCloseHandler = True

    print('Start of Trading Day')
    
    _buyParseIndex = 0
    while _buyParseIndex < len(_omsBuyOrderList):
        _dateDiff = datetime.date.today() - _omsBuyOrderList[_buyParseIndex]._orderDateTime.date()
        if not _dateDiff.days == 0:
            _omsBuyOrderList[_buyParseIndex]._timeInForceRemaining = _omsBuyOrderList[_buyParseIndex]._timeInForceRemaining - 1
        _buyParseIndex = _buyParseIndex + 1

    _sellParseIndex = 0
    while _sellParseIndex < len(_omsSellOrderList):
        _dateDiff = datetime.date.today() - _omsSellOrderList[_sellParseIndex]._orderDateTime.date()
        if not _dateDiff.days == 0:
            _omsSellOrderList[_sellParseIndex]._timeInForceRemaining = _omsSellOrderList[_sellParseIndex]._timeInForceRemaining - 1
        _sellParseIndex = _sellParseIndex + 1

    print('\nBuy Order Queue:')
    printUpdatedOrderQueue(_omsBuyOrderList)
    print('\nSell Order Queue:')
    printUpdatedOrderQueue(_omsSellOrderList)
    _orderQueueAccessLock.release()

def _tradingDayCloseHandler():
    _orderQueueAccessLock.acquire()

    global _omsBuyOrderList
    global _omsSellOrderList
    global _scheduleTradingDayStartHandler
    global _scheduleTradingDayCloseHandler
    
    _scheduleTradingDayStartHandler = True
    _scheduleTradingDayCloseHandler = False

    print('End of Trading Day')
    
    _buyParseIndex = 0
    while _buyParseIndex < len(_omsBuyOrderList):
        if _omsBuyOrderList[_buyParseIndex]._timeInForceRemaining == 0:
            del _omsBuyOrderList[_buyParseIndex]
            _buyParseIndex = _buyParseIndex - 1
        _buyParseIndex = _buyParseIndex + 1

    _sellParseIndex = 0
    while _sellParseIndex < len(_omsSellOrderList):
        if _omsSellOrderList[_sellParseIndex]._timeInForceRemaining == 0:
            del _omsSellOrderList[_sellParseIndex]
            _sellParseIndex = _sellParseIndex - 1
        _sellParseIndex = _sellParseIndex + 1

    print('\nBuy Order Queue:')
    printUpdatedOrderQueue(_omsBuyOrderList)
    print('\nSell Order Queue:')
    printUpdatedOrderQueue(_omsSellOrderList)
    _orderQueueAccessLock.release()

def addToOrderList(_orderList, _newRcvdOrder):
    _orderQueueAccessLock.acquire()
    if not isinstance(_newRcvdOrder, BTS_Order):
        print('Something is wrong. Check.')
        _orderQueueAccessLock.release()
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
                                if (_orderList[_listIndex]._fulfilmentType == 'all-or-nothing' and _newRcvdOrder._fulfilmentType == 'partial'):
                                    print('Order added at index {0}.'.format(_listIndex))
                                    _orderList.insert(_listIndex, _newRcvdOrder)
                                    break
                                elif (_orderList[_listIndex]._fulfilmentType == 'partial' and _newRcvdOrder._fulfilmentType == 'all-or-nothing'):
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
                                if (_orderList[_listIndex]._fulfilmentType == 'all-or-nothing' and _newRcvdOrder._fulfilmentType == 'partial'):
                                    print('Order added at index {0}.'.format(_listIndex))
                                    _orderList.insert(_listIndex, _newRcvdOrder)
                                    break
                                elif (_orderList[_listIndex]._fulfilmentType == 'partial' and _newRcvdOrder._fulfilmentType == 'all-or-nothing'):
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
    _orderQueueAccessLock.release()

def oms_scheduler():
    global _scheduleTradingDayStartHandler
    global _scheduleTradingDayCloseHandler
    
    print('Scheduler thread started')
    _omsScheduler = scheduler(time.time, time.sleep)
    _omsTime = datetime.datetime.now()
    _omsDate = _omsTime.date()
    _omsOpeningTime = datetime.datetime.combine(_omsDate, _tradingDayOpeningTime)
    _omsClosingTime = datetime.datetime.combine(_omsDate, _tradingDayClosingTime)

    _openingTimeDiff = _omsTime - _omsOpeningTime
    _closingTimeDiff = _omsClosingTime - _omsTime

    if _openingTimeDiff.days < 0:
        _scheduleTradingDayStartHandler = True
    else:
        if _closingTimeDiff.days < 0:
            _scheduleTradingDayStartHandler = True
            _omsDate = _omsDate + datetime.timedelta(1)
            _omsOpeningTime = datetime.datetime.combine(_omsDate, _tradingDayOpeningTime)
        else:
            _scheduleTradingDayCloseHandler = True
        while True:
            if _scheduleTradingDayStartHandler:
                _omsScheduler.enterabs(_omsOpeningTime.timestamp(), 1, _tradingDayStartHandler)
                _omsClosingTime = datetime.datetime.combine(_omsDate, _tradingDayClosingTime)
                print('TradingDayStartHandler Scheduled')
            elif _scheduleTradingDayCloseHandler:
                _omsScheduler.enterabs(_omsClosingTime.timestamp(), 1, _tradingDayCloseHandler)
                _omsDate = _omsDate + datetime.timedelta(1)
                _omsOpeningTime = datetime.datetime.combine(_omsDate, _tradingDayOpeningTime)
                print('TradingDayCloseHandler Scheduled')
                
            _scheduleTradingDayStartHandler = False
            _scheduleTradingDayCloseHandler = False
            
            _omsScheduler.run()

def oms_order_listener():
    global _omsBuyOrderList
    global _omsSellOrderList

    print('Starting Order Listener')
    _oms_socket = socket.socket()
    _oms_port = 6667
    _oms_socket.bind(('', _oms_port))
    print('Socket binded to %s' %(_oms_port))
    _oms_socket.listen(10)
    print('Socket is listening')
    while True:
        #Loop Initialization
        _oms_client, _oms_cli_addr = _oms_socket.accept()
        print('\nNew Order\n')
        _participantId = 0
        _orderType = 8
        _orderQuantity = 0
        _limitPrice = 0
        _minPartialFillQty = 0
        _timeInForceRemaining = 0
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
        _oTIFRemaining = _oms_client.recv(4)
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
        _timeInForceRemaining = struct.unpack('i', _oTIFRemaining)[0]
        _orderYear = struct.unpack('i', _oYear)[0]
        _orderMonth = struct.unpack('i', _oMonth)[0]
        _orderDay = struct.unpack('i', _oDay)[0]
        _orderHour = struct.unpack('i', _oHour)[0]
        _orderMinute = struct.unpack('i', _oMinute)[0]
        _orderSecond = struct.unpack('i', _oSecond)[0]
        _orderMicroSecond = struct.unpack('i', _oMicroSecond)[0]

        _orderDateTime = datetime.datetime(_orderYear, _orderMonth, _orderDay, _orderHour, _orderMinute, _orderSecond, _orderMicroSecond, None)
        print(_orderDateTime)

        _newOrder = BTS_Order(_participantId, _orderType, _orderQuantity, _limitPrice, _minPartialFillQty, _timeInForceRemaining, _orderDateTime)

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

def oms_quote_listener():
    global _omsBuyOrderList
    global _omsSellOrderList

    print('Starting Quote Listener')
    _oms_socket = socket.socket()
    _oms_port = 6666
    _oms_socket.bind(('', _oms_port))
    print('Socket binded to %s' %(_oms_port))
    _oms_socket.listen(10)
    print('Socket is listening')
    
    while True:
        #Loop Initialization
        _oms_client, _oms_cli_addr = _oms_socket.accept()
        print('\nNew Quote\n')
        _participantId = 0
        _bidPrice = 0
        _bidSize = 0
        _askPrice = 0
        _askSize = 0
        _minPartialFillQty = 0
        _timeInForceRemaining = 0
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
        _bprice = _oms_client.recv(4)
        _bsize = _oms_client.recv(4)
        _aprice = _oms_client.recv(4)
        _asize = _oms_client.recv(4)
        _minParFillQty = _oms_client.recv(4)
        _oTIFRemaining = _oms_client.recv(4)
        _oYear = _oms_client.recv(4)
        _oMonth = _oms_client.recv(4)
        _oDay = _oms_client.recv(4)
        _oHour = _oms_client.recv(4)
        _oMinute = _oms_client.recv(4)
        _oSecond = _oms_client.recv(4)
        _oMicroSecond = _oms_client.recv(4)
        
        #Unpacking received data into correct structures
        _participantId = struct.unpack('i', _pId)[0]
        _bidPrice = struct.unpack('f', _bprice)[0]
        _bidSize = struct.unpack('i', _bsize)[0]
        _askPrice = struct.unpack('f', _aprice)[0]
        _askSize = struct.unpack('i', _asize)[0]
        _minPartialFillQty = struct.unpack('i', _minParFillQty)[0]
        _timeInForceRemaining = struct.unpack('i', _oTIFRemaining)[0]
        _orderYear = struct.unpack('i', _oYear)[0]
        _orderMonth = struct.unpack('i', _oMonth)[0]
        _orderDay = struct.unpack('i', _oDay)[0]
        _orderHour = struct.unpack('i', _oHour)[0]
        _orderMinute = struct.unpack('i', _oMinute)[0]
        _orderSecond = struct.unpack('i', _oSecond)[0]
        _orderMicroSecond = struct.unpack('i', _oMicroSecond)[0]

        _quoteDateTime = datetime.datetime(_orderYear, _orderMonth, _orderDay, _orderHour, _orderMinute, _orderSecond, _orderMicroSecond, None)
        print(_quoteDateTime)

        _newQuote = BTS_Quote(_participantId, _bidPrice, _bidSize, _askPrice, _askSize, _minPartialFillQty, _timeInForceRemaining, _quoteDateTime)

        if not _omsSellOrderList:
            print('Adding to {0} order queue...'.format(_newQuote._buyOrder._orderPosition))
            if not _omsBuyOrderList:
                _omsBuyOrderList.append(_newQuote._buyOrder)
            else:
                addToOrderList(_omsBuyOrderList, _newQuote._buyOrder)
            printUpdatedOrderQueue(_omsBuyOrderList)
        else:
            _matchedIndices = _newQuote._buyOrder.check_for_match(_omsSellOrderList)
            if _matchedIndices is None:
                if not _omsBuyOrderList:
                    _omsBuyOrderList.append(_newQuote._buyOrder)
                else:
                    addToOrderList(_omsBuyOrderList, _newQuote._buyOrder)
                printUpdatedOrderQueue(_omsBuyOrderList)
            else:
                print(_matchedIndices)
                updateOrderQueue(_omsSellOrderList, _matchedIndices)
                if _newQuote._buyOrder._orderQty != 0:
                    addToOrderList(_omsBuyOrderList, _newQuote._buyOrder)
                    printUpdatedOrderQueue(_omsBuyOrderList)

        if not _omsBuyOrderList:
            print('Adding to {0} order queue...'.format(_newQuote._sellOrder._orderPosition))
            if not _omsSellOrderList:
                _omsSellOrderList.append(_newQuote._sellOrder)
            else:
                addToOrderList(_omsSellOrderList, _newQuote._sellOrder)
            printUpdatedOrderQueue(_omsSellOrderList)
        else:
            _matchedIndices = _newQuote._sellOrder.check_for_match(_omsBuyOrderList)
            if _matchedIndices is None:
                if not _omsSellOrderList:
                    _omsSellOrderList.append(_newQuote._sellOrder)
                else:
                    addToOrderList(_omsSellOrderList, _newQuote._sellOrder)
                printUpdatedOrderQueue(_omsSellOrderList)
            else:
                print(_matchedIndices)
                updateOrderQueue(_omsBuyOrderList, _matchedIndices)
                if _newQuote._sellOrder._orderQty != 0:
                    addToOrderList(_omsSellOrderList, _newQuote._sellOrder)
                    printUpdatedOrderQueue(_omsSellOrderList)
            
def start_oms_server():
    
    _schedulerThread = Thread(None, oms_scheduler, 'omsScheduler')
    _schedulerThread.start()

    _orderListenerThread = Thread(None, oms_order_listener, 'orderListener')
    _orderListenerThread.start()

    _quoteListenerThread = Thread(None, oms_quote_listener, 'quoteListener')
    _quoteListenerThread.start()
    
    while _schedulerThread.is_alive():
        if not _orderListenerThread.is_alive():
            print('Order Listener not working. Closing OMS...')
            sys.exit()
        if not _quoteListenerThread.is_alive():
            print('Quote Listener not working. Closing OMS...')
            sys.exit()
        
    print('Scheduler thread not alive. Closing OMS...')
    sys.exit()
    
start_oms_server()
