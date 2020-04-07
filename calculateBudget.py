import datetime
import json
from calendar import monthrange
from math import ceil
 
def main():

    # Load the budgeting data
    with open('BudgetingData.json') as json_data:
        financeData = json.load(json_data)

    # Tracking variable for the budget
    budget = 0

    # For loop for the various adjustment factors used to determine a stable budget
    for adjustmentFactor in [100, -50, 10, -1, 0.1, -0.05, 0.01]:
        # Loop until the stable result matches the +/- value of the adjustment
        # This mesas that positive adjustments are expected to be stable and 
        # negative adjustments are expected to be unstable
        #
        # The idea is to over/undershoot until an exact stable budget is hit
        while True:
            if isStable(financeData, budget) == (adjustmentFactor > 0):
                break
            else:
                budget += adjustmentFactor

    print ("Putting aside ${} each paycheck will be financially stable".format(ceil(budget)))
 
def isStable(financeData, budget):

    # Parse the expenses from the JSON file
    expenses = {}
    for expense in financeData["Expenses"].keys():
        expenses[expense] = {}
        expenses[expense]["effectiveDay"] = datetime.datetime.strptime(financeData["Expenses"][expense]["Start"],
                                                                        "%Y-%m-%d").date()
        expenses[expense]["lastDay"] = datetime.datetime.strptime(financeData["Expenses"][expense]["End"],
                                                                        "%Y-%m-%d").date()
        expenses[expense]["Amount"] = financeData["Expenses"][expense]["Amount"]
        expenses[expense]["Frequency"] = financeData["Expenses"][expense]["Frequency"]

    # Capture today's date
    dateitr = datetime.date.today()
 
    # Pull the starting cash
    startingCash = financeData["CurrentCash"]
    currentCash = startingCash

    # Capture paycheck information
    payDay = datetime.datetime.strptime(financeData["LastPayDate"],"%Y-%m-%d").date()
    payFrequency = financeData["PayFrequency"]
    endPay = datetime.date(9999, 1, 1)
 
    # Used to track if overall budget is decreasing over time 
    endYear = dateitr.year + 5
    startYear = dateitr.year
    yearMinimums = []
    currentYearMinimum = startingCash

    # Iterate, day by day, paying all expenses and putting aside money as is required
    # on a day-by-day basis.
    while dateitr.year < endYear:

        for itr in expenses:
            if isEffectiveToday(dateitr, expenses[itr]["effectiveDay"], 
                                expenses[itr]["lastDay"], expenses[itr]["Frequency"]):
                currentCash -= expenses[itr]["Amount"]
                if currentCash < currentYearMinimum:
                    currentYearMinimum = currentCash
           
        if currentCash < 0:
                return False

        if isEffectiveToday(dateitr, payDay, endPay, payFrequency):
                currentCash += budget
        
        dateitr += datetime.timedelta(days=1)

        # On the first of each year put aside the lowest balance for the year
        if dateitr.month is 1 and dateitr.day is 1:
            yearMinimums.append(currentYearMinimum)
            currentYearMinimum = currentCash

    # After 5 years if the current cash never went below 0 AND if the low is
    # gradually increasing the current budget is financially stable.
    #
    # The secondary condition is to make sure that over time the current cash
    # would never run out. Rather, it should slowly increase.
    return yearMinimums[0] < yearMinimums[-1]

def isEffectiveToday(currentDate, firstDate, lastDate, frequency):

    if currentDate <= firstDate or currentDate > lastDate:
        return False

    if "Y" == frequency:
        if currentDate.month == firstDate.month and isEffectiveToday(currentDate, firstDate, lastDate, "M"):
            return True
        else:
            return False
    elif "M" == frequency:
        if currentDate.day == firstDate.day:
            return True
        elif (currentDate.day < firstDate.day) and (currentDate.day == monthrange(currentDate.year, 
                                                                                    currentDate.month)):
            return True
        else:
            return False
    elif "B" == frequency:
        if ((currentDate - firstDate).days % 14) == 0:
            return True
        else:
            return False
    elif "W" == frequency:
        if ((currentDate - firstDate).days % 7) == 0:
            return True
        else:
            return False
    elif "D" == frequency:
        return False
    else:
        raise ValueError('Unknown frequency: ' + frequency)


if __name__ == "__main__":
    main()