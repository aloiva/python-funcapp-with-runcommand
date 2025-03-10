import time
import azure.functions as func
import logging
import datetime
import subprocess
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def run_command(command):
    logging.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True, timeout=5)
        logging.info(f"Command executed successfully. Output: {result.stdout}")
        return result.stdout, result.stderr
    except Exception as e:
        logging.info(f"Command failed with error: {e.stderr}")
        return e.stdout, e.stderr

@app.route(route="httptrigger", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def httptrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    command = req.params.get('command')
    if command:
        stdout, stderr = run_command(command)
        if stderr:
            return func.HttpResponse(f"Error:\n{stderr}", status_code=500)
        return func.HttpResponse(f"Output:\n{stdout}\nError:\n{stderr}")

    clearcache = req.params.get('clearcache')
    if clearcache == 'true':
        res = f"TZ: {os.environ.get('TZ')}\nLocal time before tzset: {datetime.datetime.now()}\n"
        time.tzset()
        res += f"Local time after tzset: {datetime.datetime.now()}\n"
        return func.HttpResponse(res)

    return func.HttpResponse(f"This HTTP triggered function executed successfully at {datetime.datetime.now()}. Timezone: {datetime.datetime.now().astimezone().tzinfo}.")


@app.timer_trigger(schedule=os.getenv("TIMER_SCHEDULE") or "0 */1 * * * *", arg_name="mytimer", run_on_startup=False,
              use_monitor=False) 
def timer_trigger(mytimer: func.TimerRequest) -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')