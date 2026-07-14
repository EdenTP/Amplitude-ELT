from datetime import datetime, timedelta

#start and end must be in format 'YYYYMMDDTHH' (e.g. 20260706T00)
def daily_chunks_generator(start, end):
    start_dt = datetime.strptime(start, '%Y%m%dT%H')
    end_dt = datetime.strptime(end, '%Y%m%dT%H')
    daily_chunks = []
    current_start = start_dt

    #While loop to create array of time arguments
    while current_start <= end_dt:
        # Default end of day is hour 23
        end_of_day = current_start.replace(hour=23)
        
        # If the end of the day is bigger than the set end date time, select the less of the 2
        current_end = min(end_of_day, end_dt) 
        
        # Storing the daily chunks as in string format needed for API an array of 2s
        daily_chunks.append((
            current_start.strftime('%Y%m%dT%H'),
            current_end.strftime('%Y%m%dT%H')
        ))
        
        # Step forward to 00:00 of the next day
        current_start = end_of_day + timedelta(hours=1)


    return daily_chunks