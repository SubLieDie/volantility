# -*- coding: utf-8 -*-
import threading
import os
import time
import pandas as pd



class FileData(threading.Thread):

    def __init__(self, file, *args, **kwargs):
        super(FileData, self).__init__(*args, **kwargs)
        self.file = file
        self.ticket_name = ''
        self.volatility = 0

    def run(self):
        self._open_file()

    def _open_file(self):
        with open(f'trades/{self.file}', encoding='utf8') as file:
            file_data = pd.read_csv(file, delimiter=',')
            max_price = file_data['PRICE'].max()
            min_price = file_data['PRICE'].min()
            self.ticket_name = file_data['SECID'][0]
            half_sum = (max_price + min_price) / 2
            self.volatility = round(((max_price - min_price) / half_sum) * 100, 2)


class Tickets:

    def __init__(self, folder):
        self.folder = os.listdir(folder)
        self.not_zero_dict = []
        self.zero_dict = []
        self.tickets = [FileData(file=file) for file in self.folder]

    def run(self):
        for ticket in self.tickets:
            ticket.start()
        for ticket in self.tickets:
            ticket.join()
        for ticket in self.tickets:
            self._append_dicts(volatility=ticket.volatility, ticket=ticket.ticket_name)
        self.not_zero_dict.sort(key=lambda i: i[1], reverse=True)
        self.zero_dict.sort(key=lambda i: i[-1])
        self._print_resault()

    def _append_dicts(self, volatility, ticket):
        if volatility == 0.0:
            self.zero_dict.append(ticket)
        else:
            self.not_zero_dict.append([ticket, volatility])

    def _print_resault(self):
        param_export = [['Максимальная волатильность:', 0, 3], ['Минимальная волатильность:', -4, -1],
                        'Нулевая волатильность:']
        for name, param1, param2 in param_export[:2]:
            print(f'{name}')
            for item, volatility in self.not_zero_dict[param1:param2]:
                print(f'{item} - {volatility}%')
        print(f'{param_export[2]}')
        for ticket in self.zero_dict:
            print(ticket)


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


