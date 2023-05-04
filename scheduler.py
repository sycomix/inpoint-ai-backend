import time
import logging
import schedule
import ai.utils
from timeit import default_timer
from server.analyze import analyze


# Load models once and set analyze to run only once per hour.
en_nlp, el_nlp, lang_det = ai.utils.Models.load_models()


# The wrapper function that runs analyze for the first time only.
def run_first_time():
    logging.info('ML Pipeline: First Run.')
    analyze(en_nlp, el_nlp, lang_det)
    return schedule.CancelJob


# The wrapper function which calls analyze.
def work():
    analyze(en_nlp, el_nlp, lang_det)


def scheduler(schedule_interval_secs = 60*60):

    # Run the analyze() for the first time and measure its processing time.
    start = default_timer()
    schedule.every(1).seconds.do(run_first_time)
    schedule.run_all()
    end = default_timer()
    
    # Initialize the processing time and the iteration tick.
    processing_time, tick = round(end - start), 0

    # Keep running the scheduler indefinitely, until the process is manually stopped.
    # Every loop iteration adds a few msec of timeshift.
    while True:
        if tick + processing_time >= schedule_interval_secs:
        
            # Measure the processing time.
            start = default_timer()
        
            # Schedule the job instantly, execute it and unschedule it.
            job = schedule.every(0).seconds.do(work)
            schedule.run_all()
            schedule.cancel_job(job)
        
            end = default_timer()

            # Set the new processing time and reset the tick.
            processing_time, tick = round(end - start), 0

        # Set the loop iteration to 1 sec.
        time.sleep(1)

        # The tick represents one time unit of the iteration.
        tick += 1


if __name__ == '__main__': scheduler()