import json
from datetime import date

from chardet import detect


def write_order_to_json(item, quantity, price, buyer, date_of_transaction):
    dict_to_json = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date_of_transaction}
    with open('orders.json', 'br') as f_c:  # Получение кодировки файла.
        encoding = detect(f_c.read())['encoding']
    with open('orders.json', encoding=encoding) as f_r:  # Получение словаря из файла.
        dct = json.load(f_r)
    with open('orders.json', 'w', encoding='utf-8') as f_w:
        dct['orders'] += [dict_to_json]  # Получение исходного словаря.
        json.dump(dct, f_w, indent=4, ensure_ascii=False)  # Запись данных в JSON файл


write_order_to_json('Cup', 3, 25.6, 'Orlando J. B. Bloom', f'{date.today()}')
write_order_to_json('Карандаш', 1, 0.6, 'Keanu C. Reeves', f'{date.today()}')
write_order_to_json('Велосипед', 1, 576.2, 'Николай Валуев', f'{date.today()}')
