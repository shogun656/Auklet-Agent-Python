from mock import patch

from auklet.monitoring import Monitoring
from src.benchmark import base


@patch('auklet.base.Client.update_limits')
@patch('auklet.base.Client._get_kafka_certs')
def auklet_benchmark(get_kafka_certs_mock, update_limits_mock):
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
    base.start()
    auklet_monitoring.stop()
    patcher.stop()


def control_benchmark():
    print("\n\nStarting benchmark tests without the Auklet Agent...")
    base.start()


def display_complete_results():
    """This function displays the final compared result.  Results are in table format."""
    with open('tmp/benchmark_results') as file:
        my_list = tuple(tuple(map(str, line.split())) for line in file)

    try:
        print("\n\nTest comparison for run time only of " + my_list[0][0] + " and " + my_list[3][0])
        p2(my_list[0][0].split('_')[0], my_list[3][0].split('_')[0])
        p3("seconds", "seconds", "name")
        for i in range(0, 3):
            p3(str(round(float(my_list[i][2]), 6)), str(round(float(my_list[i+3][2]), 6)), my_list[i][1])

        control_run_time = float(my_list[0][2]) + float(my_list[1][2]) + float(my_list[2][2])
        auklet_run_time = float(my_list[3][2]) + float(my_list[4][2]) + float(my_list[5][2])

        print("---")
        p3(str(round(control_run_time, 6)), str(round(auklet_run_time, 6)), "Total Run Time")
    except IndexError:
        print("Tests did not fully complete.")


def p2(column1, column2):
    print(column1, column2, sep='\t')


def p3(column_1, column_2, column_3):
    print(column_1, column_2, column_3, sep='\t')


def main():
    control_benchmark()
    auklet_benchmark()
    display_complete_results()


if __name__ == "__main__":
    main()
