def separator(num):  # Печать разделителя между заданиями
    print(f'\n{"-" * 60}\nPractice_01.0{num}:\n')


separator(1)
lst_str = ['разработка', 'сокет', 'декоратор']
lst_utf_str = ['\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
               '\u0441\u043e\u043a\u0435\u0442',
               '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
               ]
message = ['* Cтроковое представление:', '\n* Представление последовательностью юникод-кодов:']
for n in [lst_str, lst_utf_str]:
    print(message[n is lst_utf_str])
    [print(f'{n[i]} ({type(n[i])})') for i in range(len(lst_str))]

separator(2)

bite_data = [eval(f'b"{i}"') for i in ('class', 'function', 'method')]
print(*[f'type: {type(x)}, '
        f'content: {x}, '
        f'len: {len(x)}' for x in bite_data], sep='\n')  # Вывод типа, содержимого и длины.

separator(3)
no_bytes_words = []
for i in ('attribute', 'класс', 'функция', 'type'):
    try:
        x = eval(f'b"{i}"')
    except SyntaxError:
        no_bytes_words.append(i)

print(*no_bytes_words, sep='\n')  # Вывод слов, которые нельзя записать в байтовом типе.

separator(4)

initial_data = ['разработка', 'администрирование', 'protocol', 'standard']
byte_data = [str.encode(i, encoding='utf-8') for i in initial_data]
print('* To byte:', *byte_data, sep='\n')  # Вывод результатов преобразования в байтовое представление.
str_data = [bytes.decode(i, encoding='utf-8') for i in byte_data]
print('\n* To string:', *str_data, sep='\n')  # Вывод результатов преобразования в строковое представление.

separator(5)

import subprocess
import platform
import chardet

param = '-n' if platform.system().lower() == 'windows' else '-c'
for adr in ['yandex.ru', 'youtube.com']:
    args = ['ping', param, '2', adr]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in process.stdout:
        result = chardet.detect(line)
        print('result = ', result)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))

separator(6)

from chardet import detect

with open('test.txt', 'w') as file:  # Создание файла, состоящего из трех строк.
    for wrd in ['сетевое программирование', 'сокет', 'декоратор']:
        file.write(wrd + '\n')

with open('test.txt', 'rb') as file_с:  # Получение кодировки.
    content = file_с.read()
encoding = detect(content)['encoding']

with open('test.txt', encoding=encoding) as file_r:  # Чтение файла.
    content = file_r.read()
    print(content)
