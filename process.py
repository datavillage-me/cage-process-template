import logging
import time
import requests
import os
import pandas as pd
from dv_utils import default_settings, Client

logger = logging.getLogger(__name__)

# let the log go to stdout, as it will be captured by the cage operator
logging.basicConfig(
    level=default_settings.log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# define an event processing function
def event_processor(evt: dict):
    """
    Process an incoming event
    """
    start = time.time()

    try:
        logger.info(f"Processing event {evt}")

        evt_type =evt.get("type", "")
        if(evt_type == "QUOTE"):
           logger.info(f"use the update quote event processor")
           update_quote_event_processor(evt)
        else:
           logger.info(f"Unhandled message type, use the generic event processor")
           generic_event_processor(evt)

    # pylint: disable=broad-except
    except Exception as err:
        logger.error(f"Failed processing event: {err}")
    finally:
        logger.info(f"Processed event in {time.time() - start:.{3}f}s")



def generic_event_processor(evt: dict):
   client = Client()

   # Use userIds provided in the event, or get all active users for this application
   user_ids = evt.get("userIds", []) or client.get_users()   

   logger.info(f"Processing {len(user_ids)} users")
   for user_id in user_ids:
      try:
         # retrieve data graph for user
         # user_data = client.get_data(user_id) or {}

         # for the sake of this example, write some RDF with a dummy 0 count into the user's pod
         client.write_results(user_id, "inferences", f"<https://datavillage.me/{user_id}> <https://datavillage.me/count> 0" )

      # pylint: disable=broad-except
      except Exception as err:
         logger.warning(f"Failed to process user {user_id} : {err}")


def update_quote_event_processor(evt: dict):
   client = Client()

   STOCK_XL_PATH = os.environ.get("STOCK_XL_PATH", "")
   FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
   if(not STOCK_XL_PATH):
       raise RuntimeError("STOCK_XL_PATH environment variable is not defined")
   if(not FMP_API_KEY):
       raise RuntimeError("FMP_API_KEY environment variable is not defined")

   # get the stocks to quote from xlsx file
   stocks = pd.read_excel(STOCK_XL_PATH)
   stocks = stocks.set_index("symbol")

   # get the quotes for the symbol through an API call to FinancialModelingPrep
   symbols = ",".join(stocks.index)
   stock_response = requests.get(f"https://financialmodelingprep.com/api/v3/quote-short/{symbols}?apikey={FMP_API_KEY}")
   stock_quotes = stock_response.json()

   # merge quotes with symbols in a unified dataframe and possibly save it to file
   stocks = stocks.join(pd.DataFrame(stock_quotes).set_index("symbol") )
   try:
       stocks.to_excel("/resources/outputs/stocks.xlsx")
   except:
      pass

   # prepare rdf file with the quotes following schema.org onthology
   rdf_content = "".join([f"""
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Intangible/FinancialQuote> .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/additionalType> <https://schema.org/FinancialProduct> .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/tickerSymbol> "{r["symbol"]}" .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/exchange> "{r["exchange"]}" .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/name> "{r["name"]}" .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/price> "{r["price"]}"^^<http://www.w3.org/2001/XMLSchema#float> .
<https://www.google.com/finance/quote/{r["exchange"]}:{r["symbol"]}> <https://schema.org/volume> "{r["volume"]}"^^<http://www.w3.org/2001/XMLSchema#float> .
   """ for r in stocks.reset_index().to_dict("records")])
   logger.info(f"Generated RDF content:\n{rdf_content}")

   # Use userIds provided in the event, or get all active users for this application
   user_ids = evt.get("userIds",[]) or client.get_users()

   # Save the stock quotes in the data vault of all the users
   logger.info(f"Processing {len(user_ids)} users")
   for user_id in user_ids:
      try:
         # for the sake of this example, write some RDF with the number of user statements into the user's pod
         client.write_results(user_id, "inferences", rdf_content)

      # pylint: disable=broad-except
      except Exception as err:
         logger.warning(f"Failed to process user {user_id} : {err}")
