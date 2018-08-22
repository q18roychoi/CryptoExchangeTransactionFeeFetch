import sys
import os
import re
import urllib.request
import openpyxl
from datetime import datetime
from shutil import copyfile

key_url = "key_url"
key_fee_stage_and_info = "key_fee_stage_and_info"
key_deposit_way_and_fee = "key_deposit_way_and_fee"
key_fee_type = "key_fee_type"
key_maker_fee = "key_maker_fee"
key_taker_fee = "key_taker_fee"
key_find_order_reverse = "key_find_order_reverse"
manual_handle = "manual_handle"
reason_no_fee_information_on_website = "no_fee_information_on_website"
reason_fail_to_fetch = "fail_to_fetch"
reason_element_not_found_or_structure_updated = "element_not_found_or_structure_updated"

get_num = "[-]?\d+\.?\d*[ ]*[%]?"
get_fixed_value = "([-]?\d+\.?\d*[^%]$)"
get_percentage = "([-]?\d+\.?\d*[ ]*%)"

all_free_statement = "-|Free|FREE|no fee|Free for charge|N/A|Customers please bear transfer fee|※振込み手数料はお客様にてご負担ください"

free_or_fee_regex = "(" + all_free_statement + "|" + get_num + ")"
free_or_fee_regex_not_capture = "(?:" + all_free_statement + "|" + get_num + ")"

free_or_fixed_value_regex = "(" + all_free_statement + "|" + get_fixed_value + ")"
free_or_fixed_value_regex_not_capture = "(?:" + all_free_statement + "|" + get_fixed_value + ")"
free_or_percentage_regex = "(" + all_free_statement + "|" + get_percentage + ")"
free_or_percentage_regex_not_capture = "(?:" + all_free_statement + "|" + get_percentage + ")"

ignore_now = "ignore_now"

key_payment_method = "payment_method"
key_fixed_fee = "fixed_fee"
key_percent_fee = "percent_fee"
key_third_party_fixed_fee = "third_party_fixed_fee"
key_third_party_percent_fee = "third_party_percent_fee"

key_Default = "Default"
key_cash_deposit = "Cash Deposit"
key_credit_card = "Credit card"
key_wallet_deposit = "Wallet deposit"

key_HKD = "HKD"
key_USD = "USD"
key_EUR = "EUR"
key_GBP = "GBP"
key_JPY = "JPY"
key_AUD = "AUD"
key_CAD = "CAD"
key_KRW = "KRW"
key_PLN = "PLN"
key_RUB = "RUB"
key_ZAR = "ZAR"

key_BTC = "BTC"
key_ETH = "ETH"
key_LTC = "LTC"
key_USDT = "USDT"
key_XRP = "XRP"
key_EOS = "EOS"
key_IDR = "IDR"
key_DKKT = "DKKT"

key_exchange_name = "key_exchange_name"
key_fee_stage_and_fee = "key_fee_stage_and_fee"

# anxpro, bibox, bitbank, coinnest, exmo, gateio, indodax, lbank, liqui, livecoin, wex, yobit, zaif

exchange_trading_fee_from_website_by_statement = {
    "anxpro": {key_url: "https://anxpro.com/pages/fees", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: "You will be charged <b>" + free_or_fee_regex + "</b> on orders that are filled immediately (i.e. taker) regardless of whether they are submitted as limit or market order",
            key_taker_fee: "You will be charged <b>" + free_or_fee_regex + "</b> on limit orders that are resting (i.e. maker) in the market prior to being filled"
        }
    }},
    "bibox": {key_url: "https://bibox.zendesk.com/hc/en-us/articles/360002336133", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex + " Trading Fee will be deducted from your balance",
            key_taker_fee: ""
        }
    }},
    "binance": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: "General: " + free_or_fee_regex + " trading fee.",
            key_taker_fee: ""
        }
    }},
    "bitbank": {key_url: "", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "bitfinex2": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
              key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "500000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                   key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "1000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                    key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "2500000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                    key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "5000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                    key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "7500000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                    key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "10000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                     key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "15000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                     key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "20000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                     key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "25000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                     key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"},
        "30000000": {key_maker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td",
                     key_taker_fee: "td class=\"bfx-green-text col-num\">" + free_or_fee_regex + "</td"}
    }},
    "bitflye": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
              key_taker_fee: ""},
        "100000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "200000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "500000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "1000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                    key_taker_fee: ""},
        "2000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                    key_taker_fee: ""},
        "5000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                    key_taker_fee: ""},
        "10000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                     key_taker_fee: ""},
        "20000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                     key_taker_fee: ""},
        "50000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                     key_taker_fee: ""},
        "100000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                      key_taker_fee: ""},
        "500000000": {key_maker_fee: "td class=\"center\" colspan=\"2\">" + free_or_fee_regex + "</td",
                      key_taker_fee: ""}
    }},
    "bithumb": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "bitmarket": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "100": {key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "300": {key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "500": {key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "1000": {key_maker_fee: free_or_fee_regex,
                 key_taker_fee: free_or_fee_regex},
        "2000": {key_maker_fee: free_or_fee_regex,
                 key_taker_fee: free_or_fee_regex},
        "3000": {key_maker_fee: free_or_fee_regex,
                 key_taker_fee: free_or_fee_regex},
        "5000": {key_maker_fee: free_or_fee_regex,
                 key_taker_fee: free_or_fee_regex},
        "10000": {key_maker_fee: free_or_fee_regex,
                  key_taker_fee: free_or_fee_regex},
        "20000": {key_maker_fee: free_or_fee_regex,
                  key_taker_fee: free_or_fee_regex},
        "30000": {key_maker_fee: free_or_fee_regex,
                  key_taker_fee: free_or_fee_regex},
        "50000": {key_maker_fee: free_or_fee_regex,
                  key_taker_fee: free_or_fee_regex},
        "100000": {key_maker_fee: free_or_fee_regex,
                   key_taker_fee: free_or_fee_regex},
        "200000": {key_maker_fee: free_or_fee_regex,
                   key_taker_fee: free_or_fee_regex},
        "300000": {key_maker_fee: free_or_fee_regex,
                   key_taker_fee: free_or_fee_regex},
        "500000": {key_maker_fee: free_or_fee_regex,
                   key_taker_fee: free_or_fee_regex}
    }},
    "bitmex": {key_url: ignore_now, key_fee_stage_and_info: {  ###manual_handle
        "0": {key_maker_fee: "td style=\"text-align:right\">" + free_or_fee_regex + "</td",
              key_taker_fee: ""}
    }},
    "bitstamp": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "20000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "100000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "200000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "400000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "600000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "1000000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "2000000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "4000000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "20000000": {key_maker_fee: free_or_fee_regex, key_taker_fee: ""}
    }},
    "bittrex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "All trades have a " + free_or_fee_regex + " commission.",
              key_taker_fee: ""}
    }},
    "bitz": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "btcmarkets": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "td" + free_or_fee_regex + "</td", key_taker_fee: ""},
        "500": {key_maker_fee: "td" + free_or_fee_regex + "</td", key_taker_fee: ""},
        "1000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                 key_taker_fee: ""},
        "3000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                 key_taker_fee: ""},
        "9000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                 key_taker_fee: ""},
        "18000": {key_maker_fee: "td" + free_or_fee_regex + "</tdv",
                  key_taker_fee: ""},
        "40000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                  key_taker_fee: ""},
        "60000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                  key_taker_fee: ""},
        "70000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                  key_taker_fee: ""},
        "80000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                  key_taker_fee: ""},
        "90000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                  key_taker_fee: ""},
        "115000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "125000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "200000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "400000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "650000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "850000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                   key_taker_fee: ""},
        "1000000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                    key_taker_fee: ""},
        "3000000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                    key_taker_fee: ""},
        "5000000": {key_maker_fee: "td" + free_or_fee_regex + "</td",
                    key_taker_fee: ""}
    }},
    "cex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""},
        "5": {key_maker_fee: "", key_taker_fee: ""},
        "30": {key_maker_fee: "", key_taker_fee: ""},
        "50": {key_maker_fee: "", key_taker_fee: ""},
        "100": {key_maker_fee: "", key_taker_fee: ""},
        "200": {key_maker_fee: "", key_taker_fee: ""},
        "1000": {key_maker_fee: "", key_taker_fee: ""},
        "3000": {key_maker_fee: "", key_taker_fee: ""},
        "6000": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "coinfloor": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "500000": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: ""},
        "1000000": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: ""}
    }},
    "coinnest": {key_url: "", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: "", key_taker_fee: ""
        }
    }},
    "coinex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex}
    }},
    "coinone": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "100000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "1000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "5000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "10000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "20000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "30000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "40000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "50000000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex}
    }},
    "exmo": {key_url: "https://exmo.com/en/docs/fees", key_fee_stage_and_info: {
        # you should add currency later
        "0": {
            key_maker_fee: "Fee for the deal[\s\S]*?" + free_or_fee_regex + "</td>", key_taker_fee: ""
        }
    }},
    "exx": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: ""}
    }},
    "gateio": {key_url: "https://gate.io/fee", key_fee_stage_and_info: {  #################
        "0": {
            key_maker_fee: "Withdaw Daily Limi[\s\S]*?USDT[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""
        }
    }},
    "gdax": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "10000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "100000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex}
    }},
    "gemini": {key_url: ignore_now, key_fee_stage_and_info: {
        "0_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "5_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "10_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "100_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "1000_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "2000_BTC": {key_maker_fee: "", key_taker_fee: ""},
        "0_ETH": {key_maker_fee: "", key_taker_fee: ""},
        "5_ETH": {key_maker_fee: "", key_taker_fee: ""},
        "100_ETH": {key_maker_fee: "", key_taker_fee: ""},
        "1000_ETH": {key_maker_fee: "", key_taker_fee: ""},
        "10000_ETH": {key_maker_fee: "", key_taker_fee: ""},
        "20000_ETH": {key_maker_fee: "", key_taker_fee: ""}
    }},  ###manual_handle
    "hitbtc2": {key_url: ignore_now, key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},  ###manual_handle
    "huobipro": {
        key_url: "ignore_now",
        key_fee_stage_and_info: {
            "0": {key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex}
        }},
    "indodax": {key_url: "", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: "", key_taker_fee: ""
        }
    }},
    "itbit": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex + " bps", key_taker_fee: ""},
        "100": {
            key_maker_fee: free_or_fee_regex + " bps", key_taker_fee: ""},
        "500": {
            key_maker_fee: free_or_fee_regex + " bps", key_taker_fee: ""},
        "2500": {
            key_maker_fee: free_or_fee_regex + " bps", key_taker_fee: ""},
        "10000": {
            key_maker_fee: free_or_fee_regex + " bps", key_taker_fee: ""}
    }},
    "kraken": {
        key_url: "ignore_now", key_fee_stage_and_info: {  ###damn it
            "0": {key_maker_fee: "", key_taker_fee: ""},
            "500000": {key_maker_fee: "", key_taker_fee: ""},
            "1000000": {key_maker_fee: "", key_taker_fee: ""},
            "2500000": {key_maker_fee: "", key_taker_fee: ""},
            "5000000": {key_maker_fee: "", key_taker_fee: ""},
            "7500000": {key_maker_fee: "", key_taker_fee: ""},
            "10000000": {key_maker_fee: "", key_taker_fee: ""},
            "15000000": {key_maker_fee: "", key_taker_fee: ""},
            "20000000": {key_maker_fee: "", key_taker_fee: ""},
            "25000000": {key_maker_fee: "", key_taker_fee: ""},
            "30000000": {key_maker_fee: "", key_taker_fee: ""}
        }},
    "kucoin": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex + " trading fee", key_taker_fee: ""}
    }},
    "lbank": {key_url: "", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""},
        "500000": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "liqui": {key_url: "https://liqui.io/fee", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: "Fee schedule[\s\S]*?USDT[\s\S]*?" + free_or_fee_regex,
            key_taker_fee: "Fee schedule[\s\S]*?USDT[\s\S]*?" + free_or_fee_regex_not_capture + "[\s\S]*?" + free_or_fee_regex
        }
    }},
    "livecoin": {key_url: "https://www.livecoin.net/en/fees", key_fee_stage_and_info: {
        "0": {key_maker_fee: "0 - 100,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "100000": {key_maker_fee: "100,001 - 200,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "200000": {key_maker_fee: "200,001 - 400,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "400000": {key_maker_fee: "400,001 - 600,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "6000000": {key_maker_fee: "600,001 - 800,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "8500000": {key_maker_fee: "800,001 - 1,000,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "10000000": {key_maker_fee: "1,000,001 - 1,500,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "15000000": {key_maker_fee: "1,500,001 - 2,000,000$[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""},
        "20000000": {key_maker_fee: "2,000,001[\s\S]*?" + free_or_fee_regex, key_taker_fee: ""}
    }},
    "luno": {key_url: ignore_now, key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""},
        "10": {key_maker_fee: "", key_taker_fee: ""},
        "100": {key_maker_fee: "", key_taker_fee: ""}
    }},  ###manual_handle
    "okex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "600": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "1200": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "2400": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "12000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "24000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "60000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "120000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex}
    }},
    "poloniex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {
            key_maker_fee: free_or_fee_regex, key_taker_fee: free_or_fee_regex},
        "500000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "1000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "2500000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "5000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "7500000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "10000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "15000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "20000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "25000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex},
        "30000000": {
            key_maker_fee: free_or_fee_regex,
            key_taker_fee: free_or_fee_regex}
    }},
    "quadrigacx": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "quoinex": {key_url: "ignore_now", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "wex": {key_url: "https://wex.nz/fees", key_fee_stage_and_info: {
        "0": {key_maker_fee: "Trade fee[\s\S]*?" + free_or_percentage_regex, key_taker_fee: ""}
    }},
    "yobit": {key_url: "", key_fee_stage_and_info: {
        "0": {key_maker_fee: "", key_taker_fee: ""}
    }},
    "zaif": {
        key_url: "https://zaif.jp/fee", key_fee_stage_and_info: {
            "0": {key_maker_fee: "手数料について[\s\S]*?現物取引[\s\S]*?" + free_or_fee_regex + "<", key_taker_fee: ""}
        }
    }
}

deposit_fee_from_website_by_statement = {

    "anxpro": {
        key_url: "https://anxpro.com/pages/fees",
        key_deposit_way_and_fee: {
            "Hong Kong Bank Cheque": {
                key_HKD: {key_fixed_fee: "PAYMENT FEE[\s\S]*?Hong Kong Bank Cheque[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "PAYMENT FEE[\s\S]*?Hong Kong Bank Cheque[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_cash_deposit: {
                key_HKD: {key_fixed_fee: "PAYMENT FEE[\s\S]*?Cash Payment[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "PAYMENT FEE[\s\S]*?Cash Payment[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_wallet_deposit: {
                key_BTC: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bibox": {
        key_url: "https://bibox.zendesk.com/hc/en-us/articles/360002336133",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fixed_value_regex,
                           key_percent_fee: "Deposit Fee[\s\S]*?" + free_or_percentage_regex,
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fee[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fee[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fee[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fee[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "binance": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_wallet_deposit: {
                key_USDT: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fixed_value_regex,
                           key_percent_fee: "Deposit:[\s\S]?*" + free_or_percentage_regex,
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit:[\s\S]?*" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit:[\s\S]?*" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit:[\s\S]?*" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit:[\s\S]?*" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_EOS: {key_fixed_fee: "Deposit: " + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitbank": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitfinex2": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "TetherUSD (Omni)[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Ethereum[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Ripple[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Litecoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "EOS[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitflyer": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "bitWire": {
                key_BTC: {key_fixed_fee: "bitWire Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Quick deposit": {
                key_JPY: {key_fixed_fee: "Quick Deposit Fee[\s\S]*?" + free_or_fee_regex + " JPY per deposit",
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bithumb": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitmarket": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Regular transfer": {
                key_PLN: {key_fixed_fee: "Regular transfer:[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Instant transfer": {
                key_PLN: {key_fixed_fee: "Instant transfer:[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer SEPA (SHA)": {
                key_EUR: {key_fixed_fee: "Transfer SEPA (SHA):[\s\S]*?" + free_or_fee_regex + " EUR</b>",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer INT (SHA)": {
                key_EUR: {key_fixed_fee: "Transfer INT (SHA):[\s\S]*?" + free_or_fee_regex + " EUR</b>",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer INT (BEN)": {
                key_EUR: {key_fixed_fee: "Transfer INT (BEN):[\s\S]*?" + free_or_fee_regex + " EUR plus",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "Deposit[\s\S]*?BTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit[\s\S]*?LTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit[\s\S]*?XRP[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitmex": {
        key_url: ignore_now,  ###manual_handle
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitstamp": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "SEPA": {
                key_EUR: {key_fixed_fee: "SEPA[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_credit_card: {
                key_USD: {key_fixed_fee: "CREDIT CARD PURCHASE[\s\S]*?Any amount[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "International wire": {
                key_USD: {key_fixed_fee: "INTERNATIONAL WIRE[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "BITCOIN[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "RIPPLE XRP[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "LITECOIN[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "ETHEREUM[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bittrex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitz": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_DKKT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "btcmarkets": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "BPAY": {
                key_AUD: {key_fixed_fee: "Deposit Fees[\s\S]*?BPAY[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "Deposit Fees[\s\S]*?Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit Fees[\s\S]*?Ethereum[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit Fees[\s\S]*?Ripple[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit Fees[\s\S]*?Litecoin[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "cex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_credit_card: {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Bank transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "coinfloor": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USD: {key_fixed_fee: "Deposit fee[\s\S]*?US Dollar (USD)[\s\S]*?" + free_or_fee_regex + " USD",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit fee[\s\S]*?Euro (EUR)[\s\S]*?" + free_or_fee_regex + " EUR",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_GBP: {key_fixed_fee: "Deposit fee[\s\S]*?Pound Sterling (GBP)[\s\S]*?" + free_or_fee_regex + " GBP",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit fee[\s\S]*?Bitcoin (XBT)[\s\S]*?" + free_or_fee_regex + " XBT",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "coinex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?USDT[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?BTC[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?ETH[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?XRP[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?LTC[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EOS: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?EOS[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "coinnest": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "coinone": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "exmo": {
        key_url: "https://exmo.com/en/docs/fees",
        key_deposit_way_and_fee: {
            # "Money Polo": {
            #    key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"},
            #    key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"},
            #    key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"}
            # },
            "AdvCash": {
                key_USD: {key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?AdvCash[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?AdvCash[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?AdvCash[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?AdvCash[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?AdvCash[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?AdvCash[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Neteller": {
                key_USD: {key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Neteller[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Neteller[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Neteller[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Neteller[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Neteller[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Neteller[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Wire Transfer": {
                key_USD: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Wire Transfer[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Wire Transfer[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Skrill": {
                key_USD: {key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Skrill[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Skrill[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Skrill[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Skrill[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_PLN: {key_fixed_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Skrill[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Skrill[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Payeer": {
                key_USD: {key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Payeer[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Payeer[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Payeer[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Payeer[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Payeer[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Payeer[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Perfect Money": {
                key_USD: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Perfect Money[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Perfect Money[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            key_credit_card: {
                key_USD: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Visa/Master[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Visa/Master[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Visa/Master[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Visa/Master[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Visa/Master[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Visa/Master[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Crypto capital": {
                key_USD: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?CryptoCapital[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?CryptoCapital[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?CryptoCapital[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?CryptoCapital[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?CryptoCapital[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?CryptoCapital[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "SEPA": {
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?SEPA[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?SEPA[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Rapid Transfer": {
                key_EUR: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Rapid Transfer[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Rapid Transfer[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Rapid Transfer[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?PLN[\s\S]*?Rapid Transfer[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Yandex Money": {
                key_RUB: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Yandex Money[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Yandex Money[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Qiwi": {
                key_USD: {key_fixed_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Qiwi[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?USD[\s\S]*?Qiwi[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Qiwi[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?EUR[\s\S]*?Qiwi[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Qiwi[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Deposit Fees[\s\S]*?RUB[\s\S]*?Qiwi[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?USDT[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?USDT[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?BTC[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?BTC[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?ETH[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?ETH[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?XRP[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?XRP[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?LTC[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit Fees[\s\S]*?Cryptocurrency[\s\S]*?LTC[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "exx": {  #####################################################
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "提币费率[\s\S]*?USDT[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "提币费率[\s\S]*?BTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "提币费率[\s\S]*?ETH[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "提币费率[\s\S]*?LTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gateio": {
        key_url: "https://gate.io/fee",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Deposit[\s\S]*?USDT[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?USDT[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Deposit[\s\S]*?BTC[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?BTC[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Deposit[\s\S]*?ETH[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?ETH[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Deposit[\s\S]*?XRP[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?XRP[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Deposit[\s\S]*?LTC[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?LTC[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EOS: {
                    key_fixed_fee: "Deposit[\s\S]*?EOS[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Deposit[\s\S]*?EOS[\s\S]*?no-wrap fee-deposit[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gdax": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "ACH": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gemini": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Wire transfer": {
                key_USD: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Wire Transfer[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Ether[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "hitbtc2": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "huobipro": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "indodax": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_IDR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }

    },
    "itbit": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Wire Transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT Transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA Transfer": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "kraken": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "US domestic wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA bank transfer": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer Fidor": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer SMBC": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Japanese domestic bank transfer": {
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "kucoin": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "lbank": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "liqui": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "livecoin": {
        key_url: "https://www.livecoin.net/en/fees",
        key_deposit_way_and_fee: {
            "Payeer": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Payeer.com[\s\S]*?USD[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Perfect Money": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?PerfectMoney.is[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "AdvCash": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?AdvCash.com[\s\S]*?USD, EUR[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Capitalist.net": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Capitalist.net[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Bitcoin[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Ethereum[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Litecoin[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?EOS[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "luno": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "EFT": {
                key_ZAR: {key_fixed_fee: "Deposit fees[\s\S]*?ZAR[\s\S]*?EFT" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Cash deposit penalty": {
                key_ZAR: {key_fixed_fee: "Deposit fees[\s\S]*?ZAR[\s\S]*?Cash Deposit Penalty" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Card deposit EveryPay": {
                key_EUR: {key_fixed_fee: "Deposit fees[\s\S]*?EUR[\s\S]*?Card deposit via EveryPay" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA transfer": {
                key_EUR: {key_fixed_fee: "Deposit fees[\s\S]*?EUR[\s\S]*?SEPA Transfer" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {
                    key_fixed_fee: "Receive fees[\s\S]*?BTC[\s\S]*?Receive by email address or mobile number" + free_or_fee_regex,
                    key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Receive fees[\s\S]*?ETH[\s\S]*?Receive by Ethereum address" + free_or_fee_regex,
                    key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "okex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "poloniex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "quadrigacx": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Bank wire": {
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Crypto capital": {
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "quoinex": {
        key_url: ignore_now,  ###manual_handle
        key_deposit_way_and_fee: {
            key_Default: {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "wex": {
        key_url: "https://wex.nz/fees",
        key_deposit_way_and_fee: {
            "Western Union": {
                key_USD: {key_fixed_fee: "Western Union[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Western Union[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "MoneyGram": {
                key_USD: {key_fixed_fee: "MoneyGram[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "MoneyGram[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Contact": {
                key_USD: {key_fixed_fee: "Contact[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Contact[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "Cryptocurrency[\s\S]*?BTC[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?BTC[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Cryptocurrency[\s\S]*?ETH[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?ETH[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "Cryptocurrency[\s\S]*?USDT[\s\S]*?" + free_or_fixed_value_regex,
                           key_percent_fee: "Cryptocurrency[\s\S]*?USDT[\s\S]*?" + free_or_percentage_regex,
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Cryptocurrency[\s\S]*?LTC[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?LTC[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "yobit": {
        key_url: "",
        key_deposit_way_and_fee: {
            "Perfect Money": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Payeer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "AdvCash": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Capitalist.net": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Qiwi New": {
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "zaif": {
        key_url: manual_handle,###jap lang not working?
        key_deposit_way_and_fee: {
            "Bank transfer": {
                key_JPY: {
                    key_fixed_fee: "日本円入金[\s\S]*?銀行振込[\s\S]*?>" + free_or_fixed_value_regex + "<",
                    key_percent_fee: "日本円入金[\s\S]*?銀行振込[\s\S]*?>" + free_or_percentage_regex + "<",
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Pay-easy deposit": {
                key_JPY: {
                    key_fixed_fee: "ペイジー入金[\s\S]*?円以上の入金[\s\S]*?" + free_or_fixed_value_regex + "円",
                    key_percent_fee: "ペイジー入金[\s\S]*?円以上の入金[\s\S]*?" + free_or_percentage_regex + "円",
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {
                    key_fixed_fee: "日本円入金[\s\S]*?コンビニ入金[\s\S]*?円以上の入金[\s\S]*?" + free_or_fixed_value_regex + "円",
                    key_percent_fee: "日本円入金[\s\S]*?コンビニ入金[\s\S]*?円以上の入金[\s\S]*?" + free_or_percentage_regex + "円",
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "zb": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    }
}

withdrawal_fee_from_website_by_statement = {

    "anxpro": {
        key_url: "https://anxpro.com/pages/fees",
        key_deposit_way_and_fee: {
            "Hong Kong Bank Cheque": {
                key_HKD: {key_fixed_fee: "PAYMENT FEE[\s\S]*?Hong Kong Bank Cheque[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_cash_deposit: {
                key_HKD: {key_fixed_fee: "PAYMENT FEE[\s\S]*?Cash Payment[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_wallet_deposit: {
                key_BTC: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: reason_no_fee_information_on_website, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bibox": {
        key_url: "https://bibox.zendesk.com/hc/en-us/articles/360002336133",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "Withdrawal Fee[\s\S]*?USDT[\s\S]*?" + free_or_fixed_value_regex + " USDT",
                           key_percent_fee: "Withdrawal Fee[\s\S]*?USDT[\s\S]*?" + free_or_percentage_regex + " USDT",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Withdrawal Fee[\s\S]*?BTC[\s\S]*?" + free_or_fixed_value_regex + " BTC",
                          key_percent_fee: "Withdrawal Fee[\s\S]*?BTC[\s\S]*?" + free_or_percentage_regex + " BTC",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Withdrawal Fee[\s\S]*?ETH[\s\S]*?" + free_or_fixed_value_regex + " ETH",
                          key_percent_fee: "Withdrawal Fee[\s\S]*?ETH[\s\S]*?" + free_or_percentage_regex + " ETH",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Withdrawal Fee[\s\S]*?LTC[\s\S]*?" + free_or_fixed_value_regex + " LTC",
                          key_percent_fee: "Withdrawal Fee[\s\S]*?LTC[\s\S]*?" + free_or_percentage_regex + " LTC",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "Withdrawal Fee[\s\S]*?EOS[\s\S]*?" + free_or_fixed_value_regex + " EOS",
                          key_percent_fee: "Withdrawal Fee[\s\S]*?EOS[\s\S]*?" + free_or_percentage_regex + " EOS",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "binance": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_wallet_deposit: {
                key_USDT: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fee_regex, key_percent_fee: "",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit:[\s\S]?*" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_EOS: {key_fixed_fee: "Deposit: " + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitbank": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitfinex2": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "TetherUSD (Omni)[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Ethereum[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Ripple[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Litecoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "EOS[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitflyer": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "bitWire": {
                key_BTC: {key_fixed_fee: "bitWire Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Quick deposit": {
                key_JPY: {key_fixed_fee: "Quick Deposit Fee[\s\S]*?" + free_or_fee_regex + " JPY per deposit",
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bithumb": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitmarket": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Regular transfer": {
                key_PLN: {key_fixed_fee: "Regular transfer:[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Instant transfer": {
                key_PLN: {key_fixed_fee: "Instant transfer:[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer SEPA (SHA)": {
                key_EUR: {key_fixed_fee: "Transfer SEPA (SHA):[\s\S]*?" + free_or_fee_regex + " EUR</b>",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer INT (SHA)": {
                key_EUR: {key_fixed_fee: "Transfer INT (SHA):[\s\S]*?" + free_or_fee_regex + " EUR</b>",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Transfer INT (BEN)": {
                key_EUR: {key_fixed_fee: "Transfer INT (BEN):[\s\S]*?" + free_or_fee_regex + " EUR plus",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "Deposit[\s\S]*?BTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit[\s\S]*?LTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit[\s\S]*?XRP[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitmex": {
        key_url: ignore_now,  ###manual_handle
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitstamp": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "SEPA": {
                key_EUR: {key_fixed_fee: "SEPA[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_credit_card: {
                key_USD: {key_fixed_fee: "CREDIT CARD PURCHASE[\s\S]*?Any amount[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "International wire": {
                key_USD: {key_fixed_fee: "INTERNATIONAL WIRE[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "BITCOIN[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "RIPPLE XRP[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "LITECOIN[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "ETHEREUM[\s\S]*?Deposit[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bittrex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "bitz": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_DKKT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "btcmarkets": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "BPAY": {
                key_AUD: {key_fixed_fee: "Deposit Fees[\s\S]*?BPAY[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "Deposit Fees[\s\S]*?Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit Fees[\s\S]*?Ethereum[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit Fees[\s\S]*?Ripple[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit Fees[\s\S]*?Litecoin[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "cex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_credit_card: {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Bank transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "coinfloor": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USD: {key_fixed_fee: "Deposit fee[\s\S]*?US Dollar (USD)[\s\S]*?" + free_or_fee_regex + " USD",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EUR: {key_fixed_fee: "Deposit fee[\s\S]*?Euro (EUR)[\s\S]*?" + free_or_fee_regex + " EUR",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_GBP: {key_fixed_fee: "Deposit fee[\s\S]*?Pound Sterling (GBP)[\s\S]*?" + free_or_fee_regex + " GBP",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit fee[\s\S]*?Bitcoin (XBT)[\s\S]*?" + free_or_fee_regex + " XBT",
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "coinex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?USDT[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?BTC[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?ETH[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?XRP[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?LTC[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EOS: {
                    key_fixed_fee: "Deposit/Withdrawal[\s\S]*?EOS[\s\S]*?\d+[\s\S]*?\d+[\s\S]*?" + free_or_fee_regex,
                    key_percent_fee: "", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "coinnest": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "coinone": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_KRW: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "exmo": {
        key_url: "https://exmo.com/en/docs/fees",
        key_deposit_way_and_fee: {
            # "Money Polo": {
            #    key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"},
            #    key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"},
            #    key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
            #              key_third_party_percent_fee: "statement"}
            # },
            "AdvCash": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_RUB: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?AdvCash[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Neteller": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_RUB: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Neteller[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Wire Transfer": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Wire Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Wire Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Skrill": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Skrill[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Payeer": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_RUB: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Payeer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Perfect Money": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Perfect Money[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Perfect Money[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            key_credit_card: {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Visa/Master[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Crypto capital": {
                key_USD: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?USD[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?CryptoCapital[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "SEPA": {
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?SEPA[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?SEPA[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Rapid Transfer": {
                key_EUR: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Rapid Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Rapid Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_PLN: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Rapid Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?PLN[\s\S]*?Rapid Transfer[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Yandex Money": {
                key_RUB: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Yandex Money[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?EUR[\s\S]*?Yandex Money[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            "Qiwi": {
                key_RUB: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Qiwi[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?RUB[\s\S]*?Qiwi[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?USDT[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?USDT[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?BTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?BTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?ETH[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?ETH[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?XRP[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?XRP[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?LTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdrawal Fees[\s\S]*?Cryptocurrency[\s\S]*?LTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "exx": {  #####################################################
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "提币费率[\s\S]*?USDT[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "提币费率[\s\S]*?BTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "提币费率[\s\S]*?ETH[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "提币费率[\s\S]*?LTC[\s\S]*?" + free_or_fee_regex, key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gateio": {
        key_url: "https://gate.io/fee",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {
                    key_fixed_fee: "Withdraw[\s\S]*?USDT[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?USDT[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_BTC: {
                    key_fixed_fee: "Withdraw[\s\S]*?BTC[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?BTC[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Withdraw[\s\S]*?ETH[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?ETH[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_XRP: {
                    key_fixed_fee: "Withdraw[\s\S]*?XRP[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?XRP[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_LTC: {
                    key_fixed_fee: "Withdraw[\s\S]*?LTC[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?LTC[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_EOS: {
                    key_fixed_fee: "Withdraw[\s\S]*?EOS[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "Withdraw[\s\S]*?EOS[\s\S]*?no-wrap fee-withdraw[\s\S]*?" + free_or_percentage_regex,
                    key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gdax": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "ACH": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "gemini": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Wire transfer": {
                key_USD: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Wire Transfer[\s\S]*?" + free_or_fee_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Bitcoin[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "DEPOSIT FEES[\s\S]*?Ether[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "hitbtc2": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "huobipro": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "indodax": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_IDR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }

    },
    "itbit": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Wire Transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT Transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA Transfer": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "kraken": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "US domestic wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA bank transfer": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer Fidor": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SWIFT international wire transfer SMBC": {
                key_EUR: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Japanese domestic bank transfer": {
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "kucoin": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Deposit Fee[\s\S]*?" + free_or_fee_regex, key_percent_fee: "",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "lbank": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "liqui": {
        key_url: "",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "livecoin": {
        key_url: "https://www.livecoin.net/en/fees",
        key_deposit_way_and_fee: {
            "Payeer": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Payeer.com[\s\S]*?USD[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Perfect Money": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?PerfectMoney.is[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "AdvCash": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?AdvCash.com[\s\S]*?USD, EUR[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Capitalist.net": {
                key_USD: {key_fixed_fee: "",
                          key_percent_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Capitalist.net[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Bitcoin[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Ethereum[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?Litecoin[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "DEPOSIT & WITHDRAWAL FEES[\s\S]*?EOS[\s\S]*?" + free_or_percentage_regex,
                          key_percent_fee: "", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "luno": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "EFT": {
                key_ZAR: {key_fixed_fee: "Deposit fees[\s\S]*?ZAR[\s\S]*?EFT" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Cash deposit penalty": {
                key_ZAR: {key_fixed_fee: "Deposit fees[\s\S]*?ZAR[\s\S]*?Cash Deposit Penalty" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Card deposit EveryPay": {
                key_EUR: {key_fixed_fee: "Deposit fees[\s\S]*?EUR[\s\S]*?Card deposit via EveryPay" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "SEPA transfer": {
                key_EUR: {key_fixed_fee: "Deposit fees[\s\S]*?EUR[\s\S]*?SEPA Transfer" + free_or_fee_regex,
                          key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {
                    key_fixed_fee: "Receive fees[\s\S]*?BTC[\s\S]*?Receive by email address or mobile number" + free_or_fee_regex,
                    key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "Receive fees[\s\S]*?ETH[\s\S]*?Receive by Ethereum address" + free_or_fee_regex,
                    key_percent_fee: "statement", key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "okex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
            }
        }
    },
    "poloniex": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "quadrigacx": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            "Bank wire": {
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Crypto capital": {
                key_CAD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "quoinex": {
        key_url: ignore_now,  ###manual_handle
        key_deposit_way_and_fee: {
            key_Default: {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_JPY: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "wex": {
        key_url: "https://wex.nz/fees",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "Cryptocurrency[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?BTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "Cryptocurrency[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?ETH[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "Cryptocurrency[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                           key_percent_fee: "Cryptocurrency[\s\S]*?USDT[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "Cryptocurrency[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_fixed_value_regex,
                          key_percent_fee: "Cryptocurrency[\s\S]*?LTC[\s\S]*?<td>[\s\S]*?<td>[\s\S]*?" + free_or_percentage_regex,
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "yobit": {
        key_url: "",
        key_deposit_way_and_fee: {
            "Perfect Money": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Payeer": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "AdvCash": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Capitalist.net": {
                key_USD: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            "Qiwi New": {
                key_RUB: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    },
    "zaif": {  ##################################
        key_url: ignore_now,
        key_deposit_way_and_fee: {
            "Bank transfer": {
                key_JPY: {key_fixed_fee: "出金[\s\S]*?日本円の銀行振込[\s\S]*?円以上の入金[\s\S]*?" + free_or_fixed_value_regex + "円",
                          key_percent_fee: "出金[\s\S]*?日本円の銀行振込[\s\S]*?円以上の入金[\s\S]*?" + free_or_percentage_regex + "円",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            },
            key_Default: {
                key_BTC: {
                    key_fixed_fee: "出金[\s\S]*?BTC送金手数料/出金[\s\S]*?>" + free_or_fixed_value_regex_not_capture +
                                   "[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "出金[\s\S]*?BTC送金手数料/出金[\s\S]*?>" + free_or_percentage_regex_not_capture +
                                     "[\s\S]*?" + free_or_percentage_regex, key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"},
                key_ETH: {
                    key_fixed_fee: "出金[\s\S]*?ETH送金手数料/出金[\s\S]*?>" + free_or_fixed_value_regex_not_capture +
                                   "[\s\S]*?" + free_or_fixed_value_regex,
                    key_percent_fee: "出金[\s\S]*?ETH送金手数料/出金[\s\S]*?>" + free_or_percentage_regex_not_capture +
                                     "[\s\S]*?" + free_or_percentage_regex, key_third_party_fixed_fee: "statement",
                    key_third_party_percent_fee: "statement"}
            }
        }
    },
    "zb": {
        key_url: "ignore_now",
        key_deposit_way_and_fee: {
            key_Default: {
                key_BTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_USDT: {key_fixed_fee: "statement", key_percent_fee: "statement",
                           key_third_party_fixed_fee: "statement",
                           key_third_party_percent_fee: "statement"},
                key_LTC: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_ETH: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_XRP: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"},
                key_EOS: {key_fixed_fee: "statement", key_percent_fee: "statement",
                          key_third_party_fixed_fee: "statement",
                          key_third_party_percent_fee: "statement"}
            }
        }
    }
}

find_trading_fee_result = {

}

find_trading_fee_exception_reason = {
    reason_no_fee_information_on_website: [], reason_fail_to_fetch: [],
    reason_element_not_found_or_structure_updated: [], manual_handle: [], ignore_now: []
}

find_deposit_fee_result = {

}

find_deposit_fee_exception_reason = {
    reason_no_fee_information_on_website: [], reason_fail_to_fetch: [],
    reason_element_not_found_or_structure_updated: [], manual_handle: [], ignore_now: []
}

find_withdrawal_fee_result = {

}

find_withdrawal_fee_exception_reason = {
    reason_no_fee_information_on_website: [], reason_fail_to_fetch: [],
    reason_element_not_found_or_structure_updated: [], manual_handle: [], ignore_now: []
}


def print_trading_fee_result(transaction_cost_xlsx):
    find_trading_fee_exception_reason[reason_element_not_found_or_structure_updated] = set(
        find_trading_fee_exception_reason[reason_element_not_found_or_structure_updated])

    print("-----------------------------------------------------------")
    print("Trading Fee Exception")
    for reason, exchange_names in find_trading_fee_exception_reason.items():
        if len(exchange_names) > 0:
            print("--------------------------")
            print(reason + ":")
            for exchange_name in exchange_names:
                print(exchange_name)

    Exchange_cell = "Exchange"
    Lower_limit_cell = "Lower_limit"
    MakerFee_cell = "MakerFee"
    TakerFee_cell = "TakerFee"

    Exchange_column_char = None
    Lower_limit_column_char = None
    MakerFee_column_char = None
    TakerFee_column_char = None

    ws = transaction_cost_xlsx["Trading_fee"]
    first_row = list(ws.rows)[0]
    for cell in first_row:
        if cell.value == Exchange_cell:
            Exchange_column_char = cell.column
        if cell.value == Lower_limit_cell:
            Lower_limit_column_char = cell.column
        if cell.value == MakerFee_cell:
            MakerFee_column_char = cell.column
        if cell.value == TakerFee_cell:
            TakerFee_column_char = cell.column

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Trading Fee Result")
    for exchange_name, fee_stage_and_fee in find_trading_fee_result.items():

        print("++++++++++++++++++++++++++")
        print(exchange_name + ": ")

        for fee_stage, fee in fee_stage_and_fee.items():
            print("\t" + fee_stage + ": maker_fee: " + fee[key_maker_fee] + ", taker_fee: " + fee[key_taker_fee])
            for row in range(2, ws.max_row):

                exchange_name_cell = ws["{}{}".format(Exchange_column_char, row)]
                lower_limit_cell = ws["{}{}".format(Lower_limit_column_char, row)]

                if exchange_name_cell.value == exchange_name and str(lower_limit_cell.value) == fee_stage:
                    '''print("exchange_name_cell {}{}".format(Exchange_column_char, row))
                    print("lower_limit_cell {}{}".format(Lower_limit_column_char, row))
                    print("MakerFee_column_char {}{}".format(MakerFee_column_char, row))
                    print("TakerFee_column_char {}{}".format(TakerFee_column_char, row))
                    print(fee[key_maker_fee])
                    print(fee[key_taker_fee])'''

                    ws["{}{}".format(MakerFee_column_char, row)] = float(fee[key_maker_fee]) / 100
                    ws["{}{}".format(TakerFee_column_char, row)] = float(fee[key_taker_fee]) / 100

                    break


def print_deposit_fee_result(transaction_cost_xlsx):
    find_deposit_fee_exception_reason[reason_element_not_found_or_structure_updated] = set(
        find_deposit_fee_exception_reason[reason_element_not_found_or_structure_updated])

    print("-----------------------------------------------------------")
    print("Deposit Fee Exception")
    for reason, exchange_names in find_deposit_fee_exception_reason.items():
        if len(exchange_names) > 0:
            print("--------------------------")
            print(reason + ":")
            for exchange_name in exchange_names:
                print(exchange_name)

    Exchange_cell = "Exchange"
    Method_cell = "Method"
    Currency_cell = "Currency"
    Fixed_fee = "Fixed_fee"
    Percent_fee = "Percent_fee"

    Exchange_column_char = None
    Method_column_char = None
    Currency_column_char = None
    Fixed_fee_column_char = None
    Percent_fee_column_char = None

    ws = transaction_cost_xlsx["Deposit"]
    first_row = list(ws.rows)[0]
    for cell in first_row:
        if cell.value == Exchange_cell:
            Exchange_column_char = cell.column
        if cell.value == Method_cell:
            Method_column_char = cell.column
        if cell.value == Currency_cell:
            Currency_column_char = cell.column
        if cell.value == Fixed_fee:
            Fixed_fee_column_char = cell.column
        if cell.value == Percent_fee:
            Percent_fee_column_char = cell.column

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Deposit Fee Result")
    for exchange_name, fee_by_deposit_way_and_currency in find_deposit_fee_result.items():
        print("++++++++++++++++++++++++++")
        print(exchange_name + ": ")
        for deposit_way, fee_by_currency in fee_by_deposit_way_and_currency.items():
            print(deposit_way + ":")
            for currency, fee_info in fee_by_currency.items():
                print("\t" + currency + ": fixed_fee: " + str(fee_info[key_fixed_fee]) + ", percentage_fee: " +
                      str(fee_info[key_percent_fee]))

                for row in range(2, ws.max_row):

                    exchange_name_cell = ws["{}{}".format(Exchange_column_char, row)]
                    method_cell = ws["{}{}".format(Method_column_char, row)]
                    currency_cell = ws["{}{}".format(Currency_column_char, row)]

                    method_value = method_cell.value
                    if None is method_value:
                        method_value = key_Default

                    if exchange_name_cell.value == exchange_name and method_value == deposit_way and currency_cell.value == currency:
                        '''print("Exchange_column_char {}{}".format(Exchange_column_char, row))
                        print("Method_column_char {}{}".format(Method_column_char, row))
                        print("currency_cell {}{}".format(Currency_column_char, row))
                        print("Fixed_fee_column_char {}{}".format(Fixed_fee_column_char, row))
                        print("Percent_fee_column_char {}{}".format(Percent_fee_column_char, row))
                        print(float(fee_info[key_fixed_fee]) / 100)
                        print(float(fee_info[key_percent_fee]))'''

                        ws["{}{}".format(Fixed_fee_column_char, row)] = float(fee_info[key_fixed_fee]) / 100
                        ws["{}{}".format(Percent_fee_column_char, row)] = float(fee_info[key_percent_fee])

                        break


def print_withdrawal_fee_result(transaction_cost_xlsx):
    find_withdrawal_fee_exception_reason[reason_element_not_found_or_structure_updated] = set(
        find_withdrawal_fee_exception_reason[reason_element_not_found_or_structure_updated])

    print("-----------------------------------------------------------")
    print("Withdrawal Fee Exception")
    for reason, exchange_names in find_withdrawal_fee_exception_reason.items():
        if len(exchange_names) > 0:
            print("--------------------------")
            print(reason + ":")
            for exchange_name in exchange_names:
                print(exchange_name)

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Withdrawal Fee Result")
    for exchange_name, fee_by_withdrawal_way_and_currency in find_withdrawal_fee_result.items():
        print("++++++++++++++++++++++++++")
        print(exchange_name + ": ")
        for withdrawal_way, fee_by_currency in fee_by_withdrawal_way_and_currency.items():
            print(withdrawal_way + ":")
            for currency, fee_info in fee_by_currency.items():
                print("\t" + currency + ": fixed_fee: " + str(fee_info[key_fixed_fee]) + ", percentage_fee: " + str(
                    fee_info[key_percent_fee]))


def print_result(transaction_cost_xlsx):
    print_trading_fee_result(transaction_cost_xlsx)
    print_deposit_fee_result(transaction_cost_xlsx)
    print_withdrawal_fee_result(transaction_cost_xlsx)


def find_element_by_regex(exchange_name, regex, webpage_str):
    ret = None
    result = re.search(regex, webpage_str)

    if None is not result:

        ret = result.groups()[0]
        ret = ret.replace('%', '')
        ret = ret.replace(' ', '')

        if "bps" in regex:
            ret = float(ret) * 0.01
        if ret in all_free_statement:
            ret = 0


    print(exchange_name, result.span() if result is not None else "None")
    return ret


def find_trading_fee_from_webpage(exchange_name, webpage, fee_stage_and_info):
    if None is not webpage:

        full_webpage_str = webpage.read().decode("UTF-8")
        # with open(exchange_name + "_trading_fee.html", "w") as file:
        #    file.write(full_webpage_str)

        for fee_stage, maker_taker_fee_regex in fee_stage_and_info.items():

            webpage_str = full_webpage_str

            maker_fee_regex = maker_taker_fee_regex[key_maker_fee]
            taker_fee_regex = maker_taker_fee_regex[key_taker_fee]

            final_maker_fee = None
            final_taker_fee = None
            maker_taker_fee_are_the_same = 0 == len(taker_fee_regex)

            final_maker_fee = find_element_by_regex(exchange_name, maker_fee_regex, webpage_str)

            if True is maker_taker_fee_are_the_same:
                final_taker_fee = final_maker_fee
            else:
                find_element_by_regex(exchange_name, taker_fee_regex, webpage_str)

            final_fee_stage_and_fee = {
                fee_stage: {
                    key_maker_fee: str(final_maker_fee), key_taker_fee: str(final_taker_fee)
                }
            }
            if exchange_name not in find_trading_fee_result:
                find_trading_fee_result[exchange_name] = {}

            if None is not final_maker_fee and None is not final_taker_fee:
                find_trading_fee_result[exchange_name].update(final_fee_stage_and_fee)
            else:
                find_trading_fee_exception_reason[reason_element_not_found_or_structure_updated].append(exchange_name)


def find_trading_fee_function():
    for exchange_name, url_and_fee_info in exchange_trading_fee_from_website_by_statement.items():

        url = url_and_fee_info[key_url]

        if 0 is len(url):
            find_trading_fee_exception_reason[reason_no_fee_information_on_website].append(exchange_name)
            continue
        if manual_handle == url:
            find_trading_fee_exception_reason[manual_handle].append(exchange_name)
            continue
        if ignore_now == url:
            find_trading_fee_exception_reason[ignore_now].append(exchange_name)
            continue

        try:
            fee_stage_and_info = url_and_fee_info[key_fee_stage_and_info]
            webpage = urllib.request.urlopen(url)
            find_trading_fee_from_webpage(exchange_name, webpage, fee_stage_and_info)
        except urllib.error.HTTPError as e:
            find_trading_fee_exception_reason[reason_fail_to_fetch].append(exchange_name)


def find_deposit_withdrawal_fee_from_webpage(exchange_name, webpage, deposit_way_and_fee,
                                             find_deposit_withdrawal_result, find_deposit_withdrawal_exception_reason):
    if None is not webpage:

        full_webpage_str = webpage.read().decode("UTF-8")
        # with open(exchange_name + "_deposit_fee.html", "w") as file:
        #    file.write(full_webpage_str)

        for deposit_withdrawal_way, fee_by_currency_dict in deposit_way_and_fee.items():

            final_fee_by_deposit_withdrawal_way = {
                deposit_withdrawal_way: {

                }
            }

            for currency, fee_regex in fee_by_currency_dict.items():

                fixed_fee_regex = fee_regex[key_fixed_fee]
                percentage_fee_regex = fee_regex[key_percent_fee]

                if len(fixed_fee_regex) > 0:
                    final_fixed_fee = find_element_by_regex(exchange_name, fixed_fee_regex, full_webpage_str)
                else:
                    final_fixed_fee = 0

                if len(percentage_fee_regex) > 0:
                    final_percentage_fee = find_element_by_regex(exchange_name, percentage_fee_regex, full_webpage_str)
                else:
                    final_percentage_fee = 0

                final_fee_by_currency = {
                    currency: {
                        key_fixed_fee: final_fixed_fee,
                        key_percent_fee: final_percentage_fee
                    }
                }
                final_fee_by_deposit_withdrawal_way[deposit_withdrawal_way].update(final_fee_by_currency)

                if exchange_name not in find_deposit_withdrawal_result:
                    find_deposit_withdrawal_result[exchange_name] = {}

                if None is not final_fixed_fee and None is not final_percentage_fee:
                    find_deposit_withdrawal_result[exchange_name].update(final_fee_by_deposit_withdrawal_way)
                else:
                    # print(exchange_name, deposit_withdrawal_way, currency)
                    # print(fixed_fee_regex)
                    # print(percentage_fee_regex)
                    find_deposit_withdrawal_exception_reason[reason_element_not_found_or_structure_updated].append(
                        exchange_name)


def find_deposit_withdrawal_fee_function(deposit_withdrawal_fee_from_website_by_statement,
                                         find_deposit_withdrawal_result, find_deposit_withdrawal_fee_exception_reason):
    for exchange_name, url_and_fee_info in deposit_withdrawal_fee_from_website_by_statement.items():

        url = url_and_fee_info[key_url]

        if 0 is len(url):
            find_deposit_withdrawal_fee_exception_reason[reason_no_fee_information_on_website].append(exchange_name)
            continue
        if manual_handle == url:
            find_deposit_withdrawal_fee_exception_reason[manual_handle].append(exchange_name)
            continue
        if ignore_now == url:
            find_deposit_withdrawal_fee_exception_reason[ignore_now].append(exchange_name)
            continue

        try:
            deposit_withdrawal_way_and_fee = url_and_fee_info[key_deposit_way_and_fee]
            webpage = urllib.request.urlopen(url)
            find_deposit_withdrawal_fee_from_webpage(exchange_name, webpage, deposit_withdrawal_way_and_fee,
                                                     find_deposit_withdrawal_result,
                                                     find_deposit_withdrawal_fee_exception_reason)
        except urllib.error.HTTPError as e:
            find_deposit_withdrawal_fee_exception_reason[reason_fail_to_fetch].append(exchange_name)


def main():

    file_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    filename, file_extension = os.path.splitext(sys.argv[1])
    backup_file_name = filename + "_" + file_datetime + file_extension
    #copyfile(sys.argv[1], backup_file_name)

    find_trading_fee_function()
    find_deposit_withdrawal_fee_function(deposit_fee_from_website_by_statement, find_deposit_fee_result,
                                         find_deposit_fee_exception_reason)
    find_deposit_withdrawal_fee_function(withdrawal_fee_from_website_by_statement, find_withdrawal_fee_result,
                                        find_withdrawal_fee_exception_reason)

    transaction_cost_xlsx = openpyxl.load_workbook(sys.argv[1])
    print_result(transaction_cost_xlsx)
    #transaction_cost_xlsx.save(sys.argv[1])


main()
