import csv
from chardet import detect
import re


def get_data():
    fnd_data = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    sys_list = [os_prod_list := [], os_name_list := [], os_code_list := [], os_type_list := []]
    # Сделал так для повышения читабельности и исходя из требований задания,
    # но, так как имена этих списков в этом скрипте явно не вызываются,
    # то логичным было бы использование:
    # sys_list = [[] for _ in range(len(fnd_data))]
    main_data = []
    for file in ['info_1.txt', 'info_2.txt', 'info_3.txt']:  # Перебор файлов.
        with open(file, 'rb') as file_c:  # Получение кодировки файла.
            content = file_c.read()
        encoding = detect(content)['encoding']
        with open(file, encoding=encoding) as file_r:  # Получение данных из файла.
            content = file_r.read()
        [sys_list[n].append(re.search(r"" + fnd_data[n] + ":\\s+\\b(.+)", content)[1])
         for n in range(len(fnd_data))]  # Заполнение списков из sys_list.
    [main_data.append(list(x)) for x in [fnd_data, *zip(*sys_list)]]  # Заполнение 'главного списка' main_data
    return main_data


def write_to_csv(csv_file):
    with open(csv_file, 'w', encoding='utf-8') as f_w:
        f_w_writer = csv.writer(f_w, quoting=csv.QUOTE_ALL, lineterminator='\n')
        f_w_writer.writerows(get_data())


write_to_csv('new.csv')
