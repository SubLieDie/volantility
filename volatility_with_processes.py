# -*- coding: utf-8 -*-
import multiprocessing
import os
import time
from queue import Empty


class FileData(multiprocessing.Process):

    def __init__(self, file, collector, *args, **kwargs):
        super(FileData, self).__init__(*args, **kwargs)
        self.file = file
        self.collector = collector
        self.price_dict = []

    def run(self):
        self._open_file()
        self._collector_put()

    def _open_file(self):
        with open(f'trades/{self.file}', encoding='utf8') as file:
            lines = file.readlines()[1:]
            for line in lines:
                data = line.split(',')
                ticket = data[0]
                self.price_dict.append(float(data[2]))
            max_price = max(self.price_dict)
            min_price = min(self.price_dict)
            self.ticket_name = ticket
            half_sum = (max_price + min_price) / 2
            self.volatility = round(((max_price - min_price) / half_sum) * 100, 2)

    def _collector_put(self):
        if not self.collector.full():
            self.collector.put(dict(volatility=self.volatility, ticket_name=self.ticket_name))


class Tickets:

    def __init__(self, folder):
        self.folder = os.listdir(folder)
        self.not_zero_dict = []
        self.zero_dict = []
        self.collector = multiprocessing.Queue(maxsize=2)
        self.tickets = []

    def run(self):
        for item in self.folder:
            ticket = FileData(file=item, collector=self.collector)
            self.tickets.append(ticket)
        for ticket in self.tickets:
            ticket.start()
        while True:
            try:
                data = self.collector.get(timeout=0.1)
                ticket_name = data['ticket_name']
                volatility = data['volatility']
                if volatility != 0:
                    self.not_zero_dict.append([volatility, ticket_name])
                else:
                    self.zero_dict.append(ticket_name)
            except Empty:
                if not any(ticket.is_alive() for ticket in self.tickets):
                    break
        for ticket in self.tickets:
            ticket.join()
        self._print_result()

    def _print_result(self):
        self.not_zero_dict.sort(key=lambda i: i[0], reverse=True)
        print('Максимальная волатильность:')
        for volatility, ticket_name in self.not_zero_dict[0:3]:
            print(f'{ticket_name} - {volatility}%')
        self.zero_dict.sort(key=lambda i: i[-1])
        print('Минимальная волатильность:')
        for volatility, ticket_name in self.not_zero_dict[-4:-1]:
            print(f'{ticket_name} - {volatility}%')
        print('Нулевая волатильность:')
        for ticket_name in self.zero_dict:
            print(f'{ticket_name}')


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()

        result = func(*args, **kwargs)

        ended_at = time.time()
        elapsed = round(ended_at - started_at, 4)
        print(f'Функция работала {elapsed} секунд(ы)')
        return result

    return surrogate


@time_track
def main():
    start = Tickets(folder='trades')
    start.run()


if __name__ == '__main__':
    main()

