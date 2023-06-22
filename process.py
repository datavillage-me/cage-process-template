import logging
import time
import requests
import os
import pandas as pd
from dv_utils import default_settings, Client, audit_log 

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
    Exception raised by this function are handled by the default event listener and reported in the logs.
    """
    
    logger.info(f"Processing event {evt}")

    # dispatch events according to their type
    evt_type =evt.get("type", "")
    if(evt_type == "QUOTE"):
        # use the QUOTE event processor dedicated function
        logger.info(f"use the update quote event processor")
        update_quote_event_processor(evt)
    else:
        # use the GENERIC event processor function, that basicaly does nothing
        logger.info(f"Unhandled message type, use the generic event processor")
        generic_event_processor(evt)


def generic_event_processor(evt: dict):
    pass


def update_quote_event_processor(evt: dict):
   client = Client()

   # push an audit log to reccord for a long duration (6months) that a quote event has been received and processed
   audit_log("received a quote event", evt=evt_type)


   # retrieve environment variables to handle the quote events
   # the path of the file containg the stock market shares to get quote for
   # the authentication key needed to connect to the FMP financial API
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
   # instead of saving the results to a file we would also have pushed the computed data directly to an output API, a database or deltashare service.
   # to keep the template demo simple, we'll just output an excel file
   stocks = stocks.join(pd.DataFrame(stock_quotes).set_index("symbol") )
   try:
       # store the output file in /resources/outputs directory, to make it available for download later through the collaboration space APIs
       stocks.to_excel("/resources/outputs/stocks.xlsx")
   except:
      pass
  


   # The rest of the code bellow is only necessary if you want to push results in the SOLID pods of the customers associated with this collaboration space
   # Not all use cases requires interaction with the end users, so you can ignore what is bellow if you are not interested in writting to the user's SOLID pod


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

   # Use userIds provided in the event, or get all active users for this collaboration
   user_ids = evt.get("userIds",[]) or client.get_users()

   # Save the stock quotes in the data vault/pod of the concerned users
   logger.info(f"Processing {len(user_ids)} users")
   for user_id in user_ids:
      try:
         # for the sake of this example, write some RDF with the number of user statements into the user's pod
         client.write_results(user_id, "inferences", rdf_content)

      # pylint: disable=broad-except
      except Exception as err:
         logger.warning(f"Failed to process user {user_id} : {err}")
