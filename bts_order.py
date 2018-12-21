from datetime import datetime

_marketPrice = 98.753

class BTS_Order:
    _orderPosition = ''
    _stdOrderType = ''
    _orderQty = 0
    _fulfilmentType = ''
    _limitPrice = 0
    _minPartialFillQty = 0
    _orderDateTime = None
    def __init__(self, _order_type, _order_qty, _limit_price=0, _min_pfill_qty=0, _order_date_time=datetime.utcnow()):
        if _order_type < 4:
            self._orderPosition = 'buy'
        else:
            self._orderPosition = 'sell'
        if (_order_type % 2) == 1:
            self._limitPrice = _limit_price
            self._stdOrderType = 'limit'
        else:
            self._stdOrderType = 'market'
        if (int(_order_type / 2) % 2) == 1:
            self._fulfilmentType = 'all-or-nothing'
        else:
            self._fulfilmentType = 'partial'
        self._orderQty = _order_qty
        self._minPartialFillQty = _min_pfill_qty
        self._orderDateTime = _order_date_time
        
        print('Order instance created with following attributes:')
        print('Order Type: {0} {1} {2}'.format(self._orderPosition, self._stdOrderType, self._fulfilmentType))
        print('Order Quantity: %d' %(self._orderQty))
        print('Limit Price: %f' %(self._limitPrice))
        print('Minimum partial-fill quantity: %d' %(self._minPartialFillQty))

    def check_for_match(self, _match_order_list):
        _partial_order_match_found = False
        _orderListLen = len(_match_order_list)
        _parseIndex = 0
        _matchIndices = []
        _priceToUse = _match_order_list[_parseIndex]._limitPrice

        #The following logic is self-explanatory. Please refer to BondBlocks' OMS part of the FullSpecs document 
        if self._orderPosition == 'buy':
            while _parseIndex < _orderListLen:
                #Price at which the orders will match
                if _match_order_list[_parseIndex]._stdOrderType == 'market':
                    if self._stdOrderType == 'market':
                        _priceToUse = _marketPrice
                    else:
                        _priceToUse = self._limitPrice
                        
                #This logic covers both partial and all-or-nothing orders
                if ((_match_order_list[_parseIndex]._limitPrice <= self._limitPrice) or (self._stdOrderType == 'market') or
                    (_match_order_list[_parseIndex]._stdOrderType == 'market')):
                    if ((_match_order_list[_parseIndex]._orderQty >= self._minPartialFillQty) and
                        (self._orderQty >= _match_order_list[_parseIndex]._minPartialFillQty)):
                        _matchIndices.append(_parseIndex)
                        if self._orderQty > _match_order_list[_parseIndex]._orderQty:
                            print('{0} units matched @{1}'.format(_match_order_list[_parseIndex]._orderQty, _priceToUse))
                            self._orderQty = self._orderQty - _match_order_list[_parseIndex]._orderQty
                            _match_order_list[_parseIndex]._orderQty = 0
                            _partial_order_match_found = True
                            _parseIndex = _parseIndex + 1
                        else:
                            print('{0} units matched @{1}'.format(self._orderQty, _priceToUse))
                            _match_order_list[_parseIndex]._orderQty = _match_order_list[_parseIndex]._orderQty - self._orderQty
                            self._orderQty = 0
                            print('Order Matched.')
                            return _matchIndices
                    else:
                        _parseIndex = _parseIndex + 1
                    _priceToUse = _match_order_list[_parseIndex]._limitPrice
                else:
                    _parseIndex = _orderListLen
            
        else:
            while _parseIndex < _orderListLen:
                #Price at which the orders will match
                if _match_order_list[_parseIndex]._stdOrderType == 'market':
                    if self._stdOrderType == 'market':
                        _priceToUse = _marketPrice
                    else:
                        _priceToUse = self._limitPrice

                #This logic covers both partial and all-or-nothing orders
                if ((_match_order_list[_parseIndex]._limitPrice >= self._limitPrice) or (self._stdOrderType == 'market') or
                    (_match_order_list[_parseIndex]._stdOrderType == 'market')):
                    if ((_match_order_list[_parseIndex]._orderQty >= self._minPartialFillQty) and
                        (self._orderQty >= _match_order_list[_parseIndex]._minPartialFillQty)):
                        _matchIndices.append(_parseIndex)
                        if self._orderQty > _match_order_list[_parseIndex]._orderQty:
                            print('{0} units matched @{1}'.format(_match_order_list[_parseIndex]._orderQty, _priceToUse))
                            self._orderQty = self._orderQty - _match_order_list[_parseIndex]._orderQty
                            _match_order_list[_parseIndex]._orderQty = 0
                            _partial_order_match_found = True
                            _parseIndex = _parseIndex + 1
                        else:
                            print('{0} units matched @{1}'.format(self._orderQty, _priceToUse))
                            _match_order_list[_parseIndex]._orderQty = _match_order_list[_parseIndex]._orderQty - self._orderQty
                            self._orderQty = 0
                            print('Order Matched.')
                            return _matchIndices
                    else:
                        _parseIndex = _parseIndex + 1
                    _priceToUse = _match_order_list[_parseIndex]._limitPrice
                else:
                    _parseIndex = _orderListLen

        if (_partial_order_match_found == False):
            print('No match found. Submitting to %s order book.' %(self._orderPosition))
        else:
            print('Submitting remaining order to %s order book.' %(self._orderPosition))
