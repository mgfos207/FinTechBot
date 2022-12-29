import robin_stocks.robinhood as rh
import pyotp
from scheduler import Scheduler
import datetime
from dateutil import tz
import pytz
import math
import time

FROM_ZONE = tz.gettz('UTC')
TO_ZONE = tz.gettz('America/New_York')

class MarketOrderBot:
  def __init__(self, creds_file):
    self.schedule = Scheduler(tzinfo=datetime.timezone.utc)
    self.creds = creds_file
    self.session = None
    self.profile = None
    self.order_details = None
    
  def login(self):
    try: # try getting token and using it otherwise do login
      lines = open(self.creds).read().splitlines()
      KEY = lines[0]
      EMAIL = lines[1]
      PASSWD = lines[2]
      CODE = pyotp.TOTP(KEY).now()
      self.session = rh.login(EMAIL, PASSWD, mfa_code=CODE)
    except Exception as e:
      print(f"Got the following error {e}")
    finally:
      self.load_user_info()
      return

  def load_user_info(self):
    self.profile = rh.load_account_profile()
    print(self.profile)
    pass

  def load_stock_info(self, stock):
    latest_stock_price = rh.get_latest_price(stock.upper())
    stock_info = rh.get_instruments_by_symbols('GPRO')

    print(latest_stock_price)
    return (latest_stock_price[0], stock_info[0]['id'])

  def prepare_order(self, ticker, dollar_buy=15):
    #get cash to spend for for
    cash = float(self.profile['cash'])
    # cash_power = cash * percent_buy
    asset_price, instrument_id = self.load_stock_info(ticker)
    if dollar_buy:
      if dollar_buy > cash or dollar_buy < float(asset_price):
        raise Exception(f"Not enough cash to purchase stock: {ticker}")
    
    quantity = math.floor(dollar_buy / float(asset_price))

    self.order_details = {
      "asset":  {
        "symbol": ticker,
        "quote": asset_price,
        'id': instrument_id,
        'order_id': None,
        'quantity': quantity
      },
      "quantity": quantity,
      "order_ids": {
        "buy": None,
        "stop_sell": None
      }
    }

    return

  def place_asset_order(self):
    try:
      ticker = self.order_details['asset']['symbol']
      quant = self.order_details['asset']['quantity']
      quote = self.order_details['asset']['quote']
      res = rh.order_buy_market(ticker, quant)
      # res = rh.order(ticker, quant, 'buy',None, float(quote) - 0.02, 'gfd')
      self.order_details['asset']['order_id'] = res['id']
      print("Response from buying asset", res)
    except Exception as e:
      print(f"Got the following error when attempting to purchase asset: {e}")

  def place_stop_loss_order(self):
    try:
      ticker = self.order_details['asset']['symbol']
      quant = self.order_details['asset']['quantity']
      stop_price = float(self.order_details['asset']['quote']) - 0.02
      res = rh.order_sell_stop_loss(ticker, quant, stop_price)
      self.order_details['order_ids']['stop_sell'] = res['id']
      print("Response from placing stop order", res)
    except Exception as e:
      print(f"Got the following error when attempting to place stop loss order: {e}")

  def place_orders(self):
    self.place_asset_order()
    self.place_stop_loss_order()
    return

  def cancel_order(self,stock_type='stop_sell'):
    order_id = self.order_details['order_id'][stock_type]
    try:
      #check if the order has already been filled
      res = rh.get_stock_order_info(order_id)
      print("Response from checking status of order", res)
      if res['state'] != 'filled':
        res = rh.cancel_stock_order(order_id)
        print("Response from cancelling order", res)
      else:
        print("No need for cancelling order it is already filled")
    except Exception as e:
      print(f"Got the following error when attempting to cancel order: {e}")

  def exit_market_order(self):
    try:
      ticker = self.order_details['asset']['symbol']
      quant = self.order_details['quantity']
      res = rh.order_sell_market(ticker, quant)
      print("Response from selling market order", res)
    except Exception as e:
      print(f"Got the following error when attempting to sell order: {e}")

  
  def schedule_market_order(self, ticker, percent_buy=1.0, dollar_amnt=15):
    est_time = pytz.timezone('US/Eastern')
    self.schedule.daily(datetime.time(hour=12, minute=8, second=40, tzinfo=est_time), self.prepare_order, args=(ticker, dollar_amnt))
    self.schedule.daily(datetime.time(hour=12, minute=8, second=50, tzinfo=est_time), self.place_orders)
    self.schedule.daily(datetime.time(hour=16, minute=29, second=30, tzinfo=est_time), self.cancel_order)
    self.schedule.daily(datetime.time(hour=16, minute=29, second=31, tzinfo=est_time), self.exit_market_order)

    while True:
      self.schedule.exec_jobs()
      time.sleep(1)

  def initialize_runs(self, ticker, dollar_buy):
    self.login()
    self.schedule_market_order(ticker, dollar_buy)


try:
  print("Logging in and getting stock and user info")
  creds_file = "/home/mgfos207/Desktop/MFORSTER_FREELANCE/FinTechBot/credsfile.txt"
  ticker = "SVIX"
  dollar_buy = 15
  rh_obj = MarketOrderBot(creds_file)
  rh_obj.initialize_runs(ticker, dollar_buy)
except Exception as e:
  print(e)
finally:
  print("Logging out the robin hood app")
  rh.logout()