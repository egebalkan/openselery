import os    
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from itertools import accumulate
import numpy as np
import json
import datetime

from openselery.collection_utils import groupBy
from openselery.github_connector import GithubConnector

def transactionToYearMonthDay(transaction):
    creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
    return f'{creation_date.day}/{creation_date.month}/{creation_date.year}'

def transactionToYearMonth(transaction):
    creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
    return f'{creation_date.month}/{creation_date.year}'

def transactionToUserEmail(transaction):
    #user_name = GithubConnector.grabUserNameByEmail(transaction["to"]["email"])
    return transaction["to"]["email"]

def transactionIsLastMonth(transaction):
    now_date = datetime.datetime.now()
    creation_date = datetime.datetime.strptime(transaction["created_at"], '%Y-%m-%dT%H:%M:%SZ')
    diff_date = now_date - creation_date
    return diff_date.total_seconds() <= 30 * 24 * 60 * 60

def transactionIsEur(transaction):
    return transaction["native_amount"]["currency"] == "EUR"

def transactionIsEurSpent(transaction):
    return float(transaction["native_amount"]["amount"]) < 0 and transactionToEur(transaction)

def transactionToEur(transaction):
    assert transaction["native_amount"]["currency"] == "EUR"
    return float(transaction["native_amount"]["amount"])

def drawBarChart(title, xlabel, keys, values):
    plt.xscale('log')
    _, diagram = plt.subplots()
    y_pos = np.arange(len(keys))*4
    diagram.barh(y_pos, values, align='center', log='true', in_layout='true' )
    diagram.set_yticks(y_pos)
    diagram.set_yticklabels(keys)
    diagram.invert_yaxis()  # labels read top-to-bottom
    diagram.set_xlabel(xlabel)
    diagram.set_title(title)
    diagram.xaxis.set_major_formatter(ScalarFormatter())

def visualizeTransactions(resultDir, transactionFilePath):
    if transactionFilePath:
        # read transactions file
        transactions_file = open(os.path.join(resultDir, transactionFilePath)).read()
        transactions = json.loads(transactions_file)

        # prepare transaction data
        data_by_day = groupBy(transactionToEur, transactions["data"]), transactionToYearMonthDay)
        spent_data_by_day_last_month = groupBy(filter(lambda t: transactionIsEurSpent(t) and transactionIsLastMonth(t), transactions["data"]), transactionToYearMonthDay)
        spent_data_by_year_month = groupBy(filter(transactionIsEurSpent, transactions["data"]), transactionToYearMonth)
        spent_data_by_user = groupBy(filter(transactionIsEurSpent, transactions["data"]), transactionToUserEmail)

        wallet_balance_btc_per_day = { k: -1 * accumulate(map(transactionToEur, v), initial = 0) for k,v in spent_data_by_day_last_month.items() }
        eur_by_day_last_month = { k: -1 * sum(map(transactionToEur, v)) for k,v in spent_data_by_day_last_month.items() }
        eur_by_year_month = { k: -1 * sum(map(transactionToEur, v)) for k,v in spent_data_by_year_month.items() }
        eur_by_user = { k: -1 * sum(map(transactionToEur, v)) for k,v in data_by_user.items() }

        # draw diagrams
        plt.rcdefaults()

        drawBarChart("BTC wallet per day in last month", "BTC", wallet_balance_btc_by_day.keys(), wallet_balance_btc_by_day.values())
        plt.savefig(resultDir + "/wallet_balance_per_day.png", bbox_inches = "tight" )

        drawBarChart("EUR transactions per day in last month", "EUR", eur_by_day_last_month.keys(), eur_by_day_last_month.values())
        plt.savefig(resultDir + "/transactions_per_day.png", bbox_inches = "tight" )

        drawBarChart("EUR transactions per month", "EUR", eur_by_year_month.keys(), eur_by_year_month.values())
        plt.savefig(resultDir + "/transactions_per_month.png", bbox_inches = "tight")

        drawBarChart("EUR transactions per user", "EUR", eur_by_user.keys(), eur_by_user.values())
        plt.savefig(resultDir + "/transactions_per_user.png", bbox_inches = "tight")


