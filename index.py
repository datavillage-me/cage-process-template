"""
Exemple file for processing dv events in a datacage and pushing the output to the user pod
"""
from dv_utils import DefaultListener

from process import event_processor, default_settings

default_settings.daemon = True
print("DEFAULT SETTINGS", default_settings)

DefaultListener(event_processor, daemon=default_settings.daemon)

