"""
Create synthetic data for the demo use case
"""

import random

import duckdb
from duckdb.typing import *

from faker import Faker



# Locales for Europe, the UK, and North America
locales = [
    # Europe
    'bg_BG',  # Bulgarian (Bulgaria)
    'cs_CZ',  # Czech (Czech Republic)
    'da_DK',  # Danish (Denmark)
    'de_AT',  # German (Austria)
    'de_CH',  # German (Switzerland)
    'de_DE',  # German (Germany)
    'el_GR',  # Greek (Greece)
    'en_IE',  # English (Ireland)
    'en_GB',  # English (United Kingdom)
    'es_ES',  # Spanish (Spain)
    'et_EE',  # Estonian (Estonia)
    'fi_FI',  # Finnish (Finland)
    'fr_BE',  # French (Belgium)
    'fr_FR',  # French (France)
    'fr_CH',  # French (Switzerland)
    'hr_HR',  # Croatian (Croatia)
    'hu_HU',  # Hungarian (Hungary)
    'it_IT',  # Italian (Italy)
    'lt_LT',  # Lithuanian (Lithuania)
    'lv_LV',  # Latvian (Latvia)
    'nl_BE',  # Dutch (Belgium)
    'nl_NL',  # Dutch (Netherlands)
    'no_NO',  # Norwegian (Norway)
    'pl_PL',  # Polish (Poland)
    'pt_PT',  # Portuguese (Portugal)
    'ro_RO',  # Romanian (Romania)
    'ru_RU',  # Russian (Russia)
    'sk_SK',  # Slovak (Slovakia)
    'sl_SI',  # Slovenian (Slovenia)
    'sv_SE',  # Swedish (Sweden)
    'uk_UA',  # Ukrainian (Ukraine)

    # UK
    'en_GB',  # English (United Kingdom)

    # North America
    'en_CA',  # English (Canada)
    'en_US',  # English (United States)
    'es_MX',  # Spanish (Mexico)
    'fr_CA',  # French (Canada)
]

currentLocale="fr_CA"

def random_id(n):
    return random.randrange(1000,9999999999999)

def random_name(n):
    i=random.randrange(0, 36)
    currentLocale=locales[i]
    fake = Faker(currentLocale)
    fake.seed_instance(int(n*10))
    return fake.name()

def random_email(n):
    i=random.randrange(0, 36)
    currentLocale=locales[i]
    fake = Faker(currentLocale)
    fake.seed_instance(int(n*10))
    return fake.unique.ascii_email()

def random_company(n):
    i=random.randrange(0, 36)
    currentLocale=locales[i]
    fake = Faker(currentLocale)
    fake.seed_instance(int(n*10))
    return fake.company()

duckdb.create_function("id", random_id, [DOUBLE], VARCHAR)
duckdb.create_function("name", random_name, [DOUBLE], VARCHAR)
duckdb.create_function("email", random_email, [DOUBLE], VARCHAR)
duckdb.create_function("company", random_company, [DOUBLE], VARCHAR)

encryption_keys = ["GZs0DsMHdXr39mzkFwHwTHvCuUlID3HB","8SX9rT9VSHohHgEz2qRer5oCoid2RUAS"]

# Generate synthetic datasets
numberOfRecords=1000
numberOfDatasets=2

for x in range(numberOfDatasets):
    res = duckdb.sql("COPY (SELECT id(i) as customer_id, name(i) as customer_name, email(i) as customer_email,company(i) as customer_company FROM generate_series(1, "+str(numberOfRecords)+") s(i)) TO 'data/customers-list"+str(x)+".parquet'  (FORMAT 'parquet')")
    key = encryption_keys[x]
    keyName="dataset"+str(x)
    res=duckdb.sql("PRAGMA add_parquet_key('"+keyName+"','"+key+"')")
    res=duckdb.sql("COPY (SELECT * FROM './data/customers-list"+str(x)+".parquet') TO './data/customers-list"+str(x)+"-encrypted.parquet' (ENCRYPTION_CONFIG {footer_key: '"+keyName+"'})")

# Read synthetic datasets
duckdb.sql("PRAGMA add_parquet_key('dataset0','"+encryption_keys[0]+"')")
duckdb.sql("PRAGMA add_parquet_key('dataset1','"+encryption_keys[1]+"')")

#check common customers on name
df = duckdb.sql("SELECT * FROM read_parquet('data/customers-list0-encrypted.parquet', encryption_config = {footer_key: 'dataset0'}) AS dataset0 JOIN (SELECT * FROM read_parquet('data/customers-list1-encrypted.parquet', encryption_config = {footer_key: 'dataset1'})) AS dataset1 ON (dataset0.customer_name=dataset1.customer_name)").df()
print (df)

#check common customers on email
df = duckdb.sql("SELECT * FROM read_parquet('data/customers-list0-encrypted.parquet', encryption_config = {footer_key: 'dataset0'}) AS dataset0 JOIN (SELECT * FROM read_parquet('data/customers-list1-encrypted.parquet', encryption_config = {footer_key: 'dataset1'})) AS dataset1 ON (dataset0.customer_email=dataset1.customer_email)").df()
print (df)

#check common contact at customers company
df = duckdb.sql("SELECT * FROM read_parquet('data/customers-list0-encrypted.parquet', encryption_config = {footer_key: 'dataset0'}) AS dataset0 JOIN (SELECT * FROM read_parquet('data/customers-list1-encrypted.parquet', encryption_config = {footer_key: 'dataset1'})) AS dataset1 ON (dataset0.customer_company=dataset1.customer_company)").df()
print (df)