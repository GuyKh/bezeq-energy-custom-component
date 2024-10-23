"""Constants for bezeq_energy."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "bezeq_energy"
ATTRIBUTION = "Data provided by http://my.bezeq.co.il/"

DAILY_USAGE_KEY = "daily_usage"
MONTHLY_USAGE_KEY = "monthly_usage"
IS_LAST_INVOICE_PAYED_KEY = "is_last_invoice_payed"
LAST_INVOICE_SUM_KEY = "last_invoice_sum"
PAYER_DETAILS_KEY = "payer_details"
MONTHLY_USED_KEY = "monthly_used"
MY_PACKAGE_KEY = "my_package"
ELEC_INVOICE_KEY = "elec_invoice"
