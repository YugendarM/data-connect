import pandas as pd
from datetime import datetime

def format_date(date):
    dt = pd.to_datetime(date)
    formatted_date = dt.strftime("%d %B")
    day = int(dt.strftime("%d"))
    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
    final_format = f"{day}{suffix} {dt.strftime('%B')}"
    return final_format