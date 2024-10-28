"""Constants for bezeq_energy."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "bezeq_energy"
ATTRIBUTION = "Data provided by http://my.bezeq.co.il/"

DAILY_USAGE_KEY = "daily_usage"
MONTHLY_USAGE_KEY = "monthly_usage"
IS_LAST_INVOICE_PAYED_KEY = "is_last_invoice_payed"
LAST_INVOICE_SUM_KEY = "last_invoice_sum"
LAST_MONTH_USAGE_KEY = "last_month_usage"
LAST_MONTH_INVOICE_KEY = "last_month_invoice"
PAYER_DETAILS_KEY = "payer_details"
MONTHLY_USED_KEY = "monthly_used"
MY_PACKAGE_KEY = "my_package"
ELEC_INVOICE_KEY = "elec_invoice"
ELEC_PAYER_KEY = "elec_payer"
UNIT_ILS = "₪"
