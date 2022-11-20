import datetime
import subprocess
import sys


def get_processes():
    output = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).stdout.readlines()
    headers = [h for h in ' '.join(output[0].decode('UTF-8').strip().split()).split() if h]
    raw_data = map(lambda s: s.decode('UTF-8').strip().split(None, len(headers) - 1), output[1:])
    return [dict(zip(headers, r)) for r in raw_data]


if __name__ == '__main__':
    res = get_processes()

    users = []
    mem = 0
    cpu = 0
    max_mem = 0
    max_cpu = 0

    for row in res:
        # Поиск уникальных пользователей
        user = next((u for u in users if u['user'] == row['USER']), None)
        if user:
            user['ctn'] += 1
        else:
            users.append(dict(user=row['USER'], ctn=1))
        # Память
        current_mem = float(row['%MEM'])
        current_cpu = float(row['%CPU'])
        mem += current_mem
        cpu += current_cpu
        if max_mem <= current_mem:
            max_mem = current_mem
            max_mem_name = row['COMMAND']
        if max_cpu <= current_cpu:
            max_cpu = current_cpu
            max_cpu_name = row['COMMAND']

    out = sys.stdout
    with open(f'./scan/{datetime.datetime.now():%d-%m-%Y-%H:%M-scan}.txt', 'w+') as f:
        sys.stdout = f
        print('Отчёт о состоянии системы:')
        print(f"Пользователи системы: "
              f"{', '.join(u['user'] for u in sorted(users, key=lambda x: x['user'], reverse=False))}")
        print(f'Процессов запущено: {len(res)}')
        print('Пользовательских процессов:')
        for user in sorted(users, key=lambda x: x['ctn'], reverse=True):
            print(f"{user['user']}: {user['ctn']}")
        print(f'Всего памяти используется: {round(mem, 2)}%')
        print(f'Всего CPU используется: {round(cpu, 2)}%')
        print(f'Больше всего памяти использует: {max_mem_name[0:20]}')
        print(f'Больше всего CPU использует: {max_cpu_name[0:20]}')
        sys.stdout = out
        f.seek(0)
        for line in f:
            print(line.strip("\n"))
