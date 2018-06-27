import sys
from auklet.monitoring import Monitoring
from pidigits import piGenerator
sys.path.append('../..')
import logging
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')


def main(number=1):
    auklet_monitoring.log("This is a test log", str)
    if(number < 10):
        my_pi = piGenerator()
        _ = [next(my_pi) for _ in range(10)]
        return main(number+1)
    else:
        return 0

auklet_monitoring = Monitoring(
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiODE2YjlkOTItYjg0Yi00OGUzLWI1ZDQtYmYwMGZiODBhOTU3IiwidXNlcm5hbWUiOiIyMjBhYzVlMy1iZGEyLTRmYmQtYTJiZi1lZDYyNWRjMGM0N2EiLCJleHAiOjE1Mjk1OTI3ODksImVtYWlsIjoiIn0.6eWsEoAnVMHkAf4Vy2-WOjxicB5KKrKBHzTFG63ZI3g",
    "jWmc4aPf5XnHHjiNbLyyNB",
    base_url="https://api-staging.auklet.io/")
auklet_monitoring.start()
# Call your main function
main()
auklet_monitoring.stop()