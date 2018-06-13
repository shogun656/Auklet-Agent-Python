from control_benchmark import control_benchmark_main
from auklet_benchmark import auklet_benchmark_main


def display_complete_results():
    with open('tmp/benchmark_results') as file:
        my_list = tuple(tuple(map(str, line.split())) for line in file)

    print("\n\nTest comparison for run time only of " + my_list[0][0] + " and " + my_list[3][0])
    p2(my_list[0][0].split('_')[0], my_list[3][0].split('_')[0])
    p3("seconds", "seconds", "name")
    for i in range(0, 3):
        p3(str(round(float(my_list[i][2]), 6)), str(round(float(my_list[i+3][2]), 6)), my_list[i][1])

    control_run_time = float(my_list[0][2]) + float(my_list[1][2]) + float(my_list[2][2])
    auklet_run_time = float(my_list[3][2]) + float(my_list[4][2]) + float(my_list[5][2])

    print("---")
    p3(str(round(control_run_time, 6)), str(round(auklet_run_time, 6)), "Total Run Time")


def p2(column1, column2):
    print(column1, column2, sep='\t')


def p3(column_1, column_2, column_3):
    print(column_1, column_2, column_3, sep='\t')


def main():
    auklet_benchmark_main()
    control_benchmark_main()
    display_complete_results()


if __name__ == "__main__":
    main()