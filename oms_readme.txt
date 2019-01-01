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
2. Give OMS client commands to place new orders.
   python3 oms_client.py order_code order_qty limit_price

   PRIORITY LOGIC VERIFICATION
   a. python3 oms_client.py 0 10000
   b. python3 oms_client.py 1 5000 95.30 (Limit order priority: Gives b higher priority over a)
   c. python3 oms_client.py 1 5000 96.00 (Price priority: Gives c higher priority over b) 
   d. python3 oms_client.py 2 5000
   e. python3 oms_client_static_timestamp.py 1 5000 95.30 (Timestamp priority: Gives e higher priority over b)
   f. python3 oms_client_static_timestamp.py 3 5000 95.30 (Prioritizing all-or-nothing orders: Gives f higher priority over e)
   g. python3 oms_client_static_timestamp.py 3 10000 95.30 (Quantity Priority: Gives g higher priority over f)

   ORDER MATCHING LOGIC VERIFICATION
   After the above commands:
   h. python3 oms_client.py 7 11000 95
   i. python3 oms_client.py 4 15000
   j. python3 oms_client.py 7 3000 95
   k. python3 oms_client_static_timestamp.py 7 11000 95

Note: You can use your own sequence of inputs to test the server logic

FOR SIMULATION:

1. To generate the script of a sequence of OMS client commands: (The example below is for a sequence of 1000 orders)
   python3 generate_client_script.py 1000
2. The command above generates a shell script with name starting with _autoOrderScript(Generated Timestamp).sh.
   To make it executable: sudo chmod 777 _autoOrderScript(Generated Timestamp).sh
3. Run: python3 oms_server.py
   In another terminal run: ./_autoOrderScript(Generated Timestamp).sh
