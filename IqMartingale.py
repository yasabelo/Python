#IMPORT IQ OPTIONS API
from iqoptionapi.api import IQOptionAPI
from iqoptionapi.stable_api import IQ_Option
#--
import numpy as np 
#--
import threading
import time as t

#LOG IN TO TRADE ACCOUNT
my_user = ""    #YOUR IQOPTION USERNAME
my_pass = ""         #YOUR IQOTION PASSWORD
#CONNECT ==>:
Iq=IQ_Option(my_user,my_pass)
iqch1,iqch2 = Iq.connect()
if iqch1==True:
    print("\nLogin successful.")
else:
    print("Log In Failed.")
#--

balance_type= "PRACTICE"    #or "REAL" 
if balance_type == 'REAL':
    Iq.change_balance(balance_type)
print("Bot started, please wait...")

start_amount=1
option_amount=start_amount
multiplier=2.5

#SET UP TRADE PARAMETERS 
Money               =   round(option_amount,2)  #Amount for Option
goal                =   "EURUSD"                #Target Instrument
size                =   60                      #Timeframe In Seconds=[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
maxdict             =   4                       #Number of Bars to look back
expirations_mode    =   1                       #Option Expiration Time in Minutes
#GET CANDLES
Iq.start_candles_stream(goal,size,maxdict)
cc=Iq.get_realtime_candles(goal,size)

#store open and close prices
my_open = []
my_close =[]
#timer for position placement
place_at  = 1                                   #time in seconds before/after bar close to place trade
def get_purchase_time():
    remaning_time=Iq.get_remaning(expirations_mode)   
    purchase_time=remaning_time
    return purchase_time

def get_expiration_time():
    exp=Iq.get_server_timestamp()
    time_to_buy=(exp % size)
    return int(time_to_buy)

def expiration_thread():
    global place_at
    while True:
        x=get_expiration_time()
        t.sleep(1)
        if x == place_at:
            place_option(Money,goal,expirations_mode)
threading.Thread(target=expiration_thread).start()

#number trades
i=0
def count_trade():
    global i
    i+=1
    return i

#get previous bar direction
def get_prev_bar_direction():
    global  prev_bar
    prev_bar=""
    global open_val
    global close_val

    for k in list(cc.keys()):
        open=(cc[k]['open'])
        close=(cc[k]['open'])

        my_open.append(open)
        open_size=len(my_open)
        open_val=my_open[open_size-2]

        my_close.append(close)
        close_size=len(my_close)
        close_val=my_close[close_size-1]

        if close_val>open_val:
            prev_bar="Bullish"
        elif close_val<open_val:
            prev_bar="Bearish"
        elif close_val == open_val:
            prev_bar="Doji"
    return prev_bar

#matingale function
def martingale(option_result):
    global Money
    global option_amount
 
    #Win
    if option_result > 0.0:                    
        option_amount=start_amount
        Money=round(option_amount,2)
    #Lose
    elif option_result < 0.0:
        #martingale
        if option_amount==option_amount:
            option_amount=round(option_amount*multiplier,2)
            option_amount=option_amount
            Money=round(option_amount,2)


def  place_option(Money,goal,expirations_mode):  
    count_trade()

    get_prev_bar_direction()

#CALL OPTION
    if prev_bar=="Bullish":
        check,id=Iq.buy(Money,goal,"call",expirations_mode)
        if check:
            print("%s.  CALL $%s : (Open: %s || Close: %s ) "%(i,Money,open_val,close_val))
            option_result=round(Iq.check_win_v3(id),2)
        #MARTINGALE
            martingale(option_result)
        else:
            print("'CALL' Option failed.")
#PUT OPTION
    elif prev_bar=="Bearish":
        check,id=Iq.buy(Money,goal,"put",expirations_mode)
        if check:
            print("%s.  PUT $%s : (Open: %s || Close: %s ) "%(i,Money,open_val,close_val))
            option_result=round(Iq.check_win_v3(id),2)
        #MARTINGALE
            martingale(option_result)
        else:
            print("'PUT' Option failed.")
    elif prev_bar=="Doji":
        print("%s. DOJI. NO OPTION PLACED. (Open: %s || Close: %s ) "%(i,open_val,close_val))
        t.sleep(Iq.get_remaning)
#FIN/END
