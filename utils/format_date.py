# from datetime import datetime
# from zoneinfo import ZoneInfo

# def format_date(date_str, from_tz='UTC', to_tz='Asia/Kolkata'):
#     dt = datetime.fromisoformat(date_str).replace(tzinfo=ZoneInfo(from_tz))
#     dt_local = dt.astimezone(ZoneInfo(to_tz))
#     day = dt_local.day
#     suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
#     formatted_date = f"{day}{suffix} {dt_local.strftime('%B')} ({to_tz})"
#     return formatted_date


from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

def format_date(date_input, from_tz='UTC', to_tz='Asia/Kolkata'):
    # Convert input to datetime if it's not already
    if isinstance(date_input, str):
        dt = datetime.fromisoformat(date_input)
    elif isinstance(date_input, pd.Timestamp):
        dt = date_input.to_pydatetime()
    elif isinstance(date_input, datetime):
        dt = date_input
    else:
        raise TypeError("Unsupported date format. Must be str, datetime, or pandas Timestamp.")
    
    # Set source timezone if not timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
    
    # Convert to target timezone
    dt_local = dt.astimezone(ZoneInfo(to_tz))
    
    # Format with suffix
    day = dt_local.day
    suffix = "th" if 4 <= day <= 20 or 24 <= day <= 30 else ["st", "nd", "rd"][day % 10 - 1]
    formatted_date = f"{day}{suffix} {dt_local.strftime('%B')} ({to_tz})"
    return formatted_date
