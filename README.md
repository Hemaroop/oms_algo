# oms_algo
A Python based Order Matching System prototype for trading securities.

README

This is an Order Matching System Prototype for securities trading. There are many things that I have not covered yet.This OMS prototype allows the users to place both separate buy & sell orders and quotes. In the current state it can be extended to all kinds of securities with some customization.

TO DO:
1. Add a mechanism for including brokerage charges and taxes. (This is going to be a lot of work!!)

ORDER CODES:
0: Buy Market Partial
1: Buy Limit Partial
2: Buy Market All-or-nothing
3: Buy Limit All-or-nothing
4: Sell Market Partial
5: Sell Limit Partial
6: Sell Market All-or-nothing
7: Sell Limit All-or-nothing

TEST SEQUENCE TO VERIFY PRIORITY AND ORDER MATCHING LOGIC:
1. Run OMS server.
   python3 oms_server.py
2. Give OMS client commands to place new orders or quotes.
   a. python3 oms_client_order.py -i participant_id -t order_code -q order_qty -l limit_price -gt time_in_force(in days)
   b. python3 oms_client_order_static_timestamp.py -i participant_id -t order_code -q order_qty -l limit_price -gt time_in_force(in days)
   c. python3 oms_client_quote.py -i participant_id --bPrice bid_price --bSize bid_size --aPrice ask_price --aSize ask_size -gt time_in_force(in days)
   d. python3 oms_client_quote_static_timestamp.py -i participant_id --bPrice bid_price --bSize bid_size --aPrice ask_price --aSize ask_size -gt time_in_force(in days)
   (NOTE: A quote is converted by the oms_server into buy limit partial and sell limit partial orders with bid_price and ask_price respectively.)

   PRIORITIZATION OF ORDERS IN THE ORDER MATCHING SYSTEM: Check for prioritization happens in the following order:
   1. Market Orders have the priority of execution. So, all market orders have higher priority over limit orders while trying to find a matching order. (NOTE: A buy market order
   cannot match with a sell market order until a market price is available through the previous orders matched.)
   2. Limit buy order with higher limit price is prioritized. Limit sell order with lower limit price is prioritized.
   3. If prices of two orders are the same, the order with earlier timestamp is prioritized.
   4. If timestamps are the same, partial-fill order is prioritized over all-or-nothing order.
   5. If orders have the same fulfilment type, order with higher quantity is given priority.
   6. If the order sizes are equal, orders from investors are given priority over orders/quotes for market makers.
   7. If everything is same for two orders, a coin toss is used to decide priority. 
   
MANUAL TESTING:
   PRIORITY LOGIC VERIFICATION
   a. python3 oms_client.py -i 32 -t 0 -q 10000
   b. python3 oms_client.py -i 73 -t 1 -q 5000 -l 95.30 (Limit order priority: Gives a higher priority over b)
   c. python3 oms_client.py -i 2 -t 1 -q 5000 -l 96.00 (Price priority: Gives c higher priority over b) 
   d. python3 oms_client.py -i 29 -t 2 -q 5000
   e. python3 oms_client_static_timestamp.py -i 7 -t 1 -q 5000 -l95.30 (Timestamp priority: Gives e higher priority over b)
   f. python3 oms_client_static_timestamp.py -i 31 -t 3 -q 5000 -l 95.30 (Prioritizing all-or-nothing orders: Gives e higher priority over f)
   g. python3 oms_client_static_timestamp.py -i 53 -t 3 -q 10000 -l 95.30 (Quantity Priority: Gives g higher priority over f)

   NOTE: You can generate your own sequence of orders to test.  

   ORDER MATCHING LOGIC VERIFICATION
   After the above commands:
   h. python3 oms_client.py -i 32 -t 7 -q 11000 -l 95
   i. python3 oms_client.py -i 79 -t 4 -q 15000
   j. python3 oms_client.py -i 83 -t 7 -q 3000 -l 95
   k. python3 oms_client_static_timestamp.py -i 65 -t 7 -q 11000 -l 95

Note: You can use your own sequence of inputs to test the server logic

AUTOMATED TESTING USING SIMULATOR:	

1. To generate the script of a sequence of OMS client commands: (The example below is for a sequence of 1000 orders)
   python3 generate_client_script.py 1000
2. The command above generates a shell script with name starting with _autoOrderScript(Generated Timestamp).sh.
   To make it executable: sudo chmod 777 _autoOrderScript(Generated Timestamp).sh
3. Run: python3 oms_server.py > omsServerLog.txt (Stores the output in a file named omsServerLog.txt)
   In another terminal run: ./_autoOrderScript(Generated Timestamp).sh

TRADING HOURS:
The trading hours are mentioned in btsTradingHours.py
DEFAULT: Starting at 0900 Hrs and closing at 1700 Hrs.
The orders arriving after closing of trade are not accepted/stored in the order book. This can be changed if required.

MINIMUM AND MAXIMUM TRADING SIZES: (This can be customized for different securities.)
These are mentioned in bts_constraints.py
Includes minimum order size (currently 1000), minimum order increment (currently 1000), maximum order increments allowed (currently 200).
