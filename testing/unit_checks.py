from prompt_util import VALID_TIME_UNITS, ValidCalendarUnits, ValidTimeUnits,deduce_elapsed_time 
from datetime import datetime, time, date, timedelta



def elapsed_time_deducer():
    b = ["5 days 15 minutes", "12 hours 188 minutes", "2 weeks 40 hours"]
    for a in b:
        print(deduce_elapsed_time(a))
    ...


def main():
    elapsed_time_deducer()
    ...


if __name__ == "__main__":
    main()



