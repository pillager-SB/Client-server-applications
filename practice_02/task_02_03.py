import yaml

lst = ['Doc Cut', 'Doc Standard', 'Doc Full']
num = 20
dct = {'price_1': '20 €', 'price_2': '50.23 €', 'price_3': '120 €'}
data_to_yaml = {'products': lst, 'version': num, 'prices': dct}

with open('file.yaml', 'w', encoding='utf-8') as f_w:  # Запись данных в файл yaml.
    yaml.dump(data_to_yaml, f_w, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open('file.yaml', encoding='utf-8') as f_r:  # Чтение данных из файла и сравнение двух словарей на идентичность.
    print('Данные', ['не совпадают', 'совпадают'][data_to_yaml == yaml.load(f_r, Loader=yaml.FullLoader)])
