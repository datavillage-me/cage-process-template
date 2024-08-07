"""
Example of a confidential workload processing data from 2 data owners and sending the results to 1 data user.
The confidential workload handles 3 events: one to perform a collaborative analysis example, one to perform a confidential AI (training the AI ​​model), and one to trigger the data owners' data quality checks.
"""

from dv_utils import DefaultListener
from process import event_processor, default_settings

default_settings.daemon = True
print("DEFAULT SETTINGS", default_settings)

DefaultListener(event_processor, daemon=default_settings.daemon)

