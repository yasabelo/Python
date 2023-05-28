#IMPORT IQ OPTIONS API
from iqoptionapi.api import IQOptionAPI
from iqoptionapi.stable_api import IQ_Option

#IMPORT NUMPY AND TALIB
import numpy as np 
import talib

#--IMPORT THREADING AND TIME (ESSENTIAL)
import threading
import time as t
#--END OF IMPORTS

#USER ACCOUNT CREDENTIALS AND LOG IN 
my_user = ""    #YOUR IQOPTION USERNAME
my_pass = ""         #YOUR IQOTION PASSWORD
#CONNECT ==>:
Iq=IQ_Option(my_user,my_pass)
iqch1,iqch2 = Iq.connect()
if iqch1==True:
    print("\nLogin successful.")
else:
    print("Log In Failed.")
#DONE

#CHOOSE BALANCE TYPE
balance_type= "PRACTICE"
if balance_type == 'REAL':
    Iq.change_balance(balance_type)
print("AI Started, Please Wait...")

#SET UP TRADE PARAMETERS 
Money               =   10                      #Amount for Option
goal                =   "EURUSD-OTC"            #Target Instrument
size                =   60                      #Timeframe In Seconds=[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
period              =   14                      #Number of Bars to look back
expirations_mode    =   1                       #Option Expiration Time in Minutes

#GET OHLC DATA FROM IQOPTION
Iq.start_candles_stream(goal,size,period)
cc=Iq.get_realtime_candles(goal,size)

#STORE OPEN AND CLOSE VALUES
my_open = []
my_close =[]

#WHEN TO PLACE BET BEFORE EXPIRY TIME (TIME IN SECONDS)
place_at  = 0
def get_purchase_time():
    remaning_time=Iq.get_remaning(expirations_mode)   
    purchase_time=remaning_time
    return purchase_time

def get_expiration_time():
    exp=Iq.get_server_timestamp()
    time_to_buy=(exp % size)
    return int(time_to_buy)

#THREAD TO RUN TIMER SIMULTANEOUSLY
def expiration_thread():
    global place_at
    while True:
        x=get_expiration_time()
        t.sleep(1)
        if x == place_at:
            place_option(Money,goal,expirations_mode)
threading.Thread(target=expiration_thread).start()

#SET VALUES TO PLACE BET(S)
def set_values():

    global open_val
    global close_val
    global ma_close_val


    for k in list(cc.keys()):
        open=(cc[k]['open'])
        close=(cc[k]['open'])

        my_open.append(open)
        open_size=len(my_open)
        open_val=my_open[open_size-2]

        my_close.append(close)
        close_size=len(my_close)
        close_val=my_close[close_size-1]

        my_ma_close=np.array(my_close)
        ma_close_values = talib.SMA(my_ma_close,timeperiod=14)
        my_ma_close_size=len(ma_close_values)
        ma_close_val = ma_close_values[my_ma_close_size-1]

#BET PLACEMENT CONDITIONS AND BET PLACEMENT
def place_option(Money,goal,expirations_mode):  
    
    set_values()

    #CALL OPTION
    if close_val>ma_close_val:
        check,id=Iq.buy(Money,goal,"call",expirations_mode)
        if check:
            print("'CALL' Option  Placed Successfully.")
        else:
            print("'CALL' Option failed.")
    #PUT OPTION
    elif close_val<ma_close_val:
        check,id=Iq.buy(Money,goal,"put",expirations_mode)
        if check:
            print("'PUT' Option  Placed Successfully.")
        else:
            print("'PUT' Option failed.")
#--END
