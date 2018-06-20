from mock import patch

from auklet.monitoring import Monitoring
from src.benchmark import base


def without_auklet():
    """
    Runs tests for a baseline number on how long the tests should take.
    """
    print("\n\nStarting benchmark tests without the Auklet Agent...")
    base.start(state="WithoutAuklet")


@patch('auklet.base.Client.update_limits')
@patch('auklet.base.Client._get_kafka_certs')
def with_auklet(get_kafka_certs_mock, update_limits_mock):
    """
    With a little help from mock, this test will push data that
    would normally go to the front end, to a kafka container created locally.
    """
    def _get_kafka_brokers(self):
        self.brokers = ["kafka:9093"]
        self.producer_types = {
            "monitoring": "profiling",
            "event": "events",
            "log": "logging"
        }
    update_limits_mock.return_value = 10000
    get_kafka_certs_mock.return_value = True

    patcher = patch('auklet.base.Client._get_kafka_brokers', new=_get_kafka_brokers)
    patcher.start()
    auklet_monitoring = Monitoring("", "", monitoring=True)
    auklet_monitoring.start()
    base.start(state="WithAuklet")
    auklet_monitoring.stop()
    patcher.stop()


def display_complete_results():
    """This function displays the final compared result.  Results are in table format."""
    with open('tmp/benchmark_results') as file:
        my_list = tuple(tuple(map(str, line.split())) for line in file)

    without_auklet_run_time = 0
    with_auklet_run_time = 0
    number_of_tests = int(len(my_list) / 2)

    try:
        print("\n\nTest comparison for run time only for with the Auklet Agent versus without the Auklet Agent")
        print(my_list[0][0].split('_')[0], my_list[number_of_tests][0].split('_')[0], sep='\t')     # Prints header
        print("seconds", "seconds", "name", "\ttimes faster without agent", sep='\t\t')

        for i in range(0, number_of_tests):     # Organizes, calculates, and prints data from file
            without_auklet = round(float(my_list[i][2]), 6)     # Individual test runtime
            with_auklet = round(float(my_list[i+number_of_tests][2]), 6)
            try:
                times_slower = round(with_auklet / without_auklet, 6)
            except ZeroDivisionError:
                times_slower = 0
            print(without_auklet, with_auklet, my_list[i][1], times_slower, sep='\t\t')

        for i in range(0, number_of_tests):     # Calculates total runtime
            without_auklet_run_time = without_auklet_run_time + float(my_list[i][2])
            with_auklet_run_time = with_auklet_run_time + float(my_list[number_of_tests+i][2])

        try:
            total_times_slower = round(with_auklet_run_time / without_auklet_run_time, 6)
        except ZeroDivisionError:
            total_times_slower = 0
        print("---")
        print(str(round(without_auklet_run_time, 6)), str(round(with_auklet_run_time, 6)), "Total Run Time", total_times_slower, sep='\t\t')
    except IndexError:
        print("Tests did not fully complete.")


def main():
    without_auklet()
    with_auklet()
    display_complete_results()


if __name__ == "__main__":
    main()
