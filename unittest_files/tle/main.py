import sys
import random
import time

i_know_answer = {
    1: "i1",
    2: "c1",
    3: "e1",
    4: "p1",
    5: "l1",
    6: "i1&e1",
    7: "i1&e2;i1&e3;i4&e5",
    8: "i1&e2;i3&e3;e4&i3",
    9: "i1&e&l42;i3&e3&l4;i5&e6&l3",
    10: "l1&e2;l3&e3;l2&e5",
}


def main():
    for line in sys.stdin:
        timestamp = int(line)
        time.sleep(random.random() + 2.5)
        print(f"{timestamp},{i_know_answer[timestamp]}", flush=True)


if __name__ == '__main__':
    main()
