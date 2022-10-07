import json
import sys
import socket
from practice_03.common.variables import *
from practice_03.common.utils import send_message, get_message


def process_client_message(message):
    """
    Функция-обработчик сообщений от клиентов, принимает словарь-сообщение,
    проверяет корректность, возвращает словарь-ответ для клиента.
    """
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}  # Запрос выполнен успешно.
    return {
        RESPONSE: 400,  # Сервер не смог понять запрос.
        ERROR: 'Bad Request'
    }


def main():
    """
    Загрузка параметров из командной строки,
    при их отсутствии - обработка значений, принятых по умолчанию.
    """
    # port:
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качестве номера порта может быть указано только число в диапазоне 1024-65535.')
        sys.exit(1)
    #  IP адрес для прослушивания.
    try:
        if '-a' in sys.argv:
            listen_address = int(sys.argv[sys.argv.index('-a') + 1])
        else:
            listen_address = ''
    except IndexError:
        print('После параметра -\'a\' необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    # Готовим сокет.
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    # Слушаем порт.
    transport.listen(MAX_CONNECTION)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except(ValueError, json.JSONDecodeError):
            print('Принято некорректное сообщение от клиента')
            client.close()


if __name__ == '__main__':
    main()
