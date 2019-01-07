from datetime import datetime
from bts_order import BTS_Order

class BTS_Quote:
    _participantId = 0
    _timeInForceRemaining = 0
    _quoteDateTime = None
    _buyOrder = None
    _sellOrder = None

    def __init__(self, _participantId, _bidPrice, _bidSize, _askPrice, _askSize, _min_pfill_qty=0, _time_In_Force_Remaining = 14, _quote_date_time=datetime.now()):
        self._participantId = _participantId
        self._timeInForceRemaining = _time_In_Force_Remaining
        self._quoteDateTime = _quote_date_time
        #Create buy, limit, partial order
        self._buyOrder = BTS_Order(_participantId, 1, _bidSize, _bidPrice, _min_pfill_qty, self._timeInForceRemaining, _quote_date_time)
        #Create sell, limit, partial order
        self._sellOrder = BTS_Order(_participantId, 5, _askSize, _askPrice, _min_pfill_qty, self._timeInForceRemaining, _quote_date_time)
