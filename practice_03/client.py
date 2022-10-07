import json
import sys
import time
import socket
from common.variables import *
from common.utils import send_message, get_message


def create_presence(account_name='Guest'):
    """Функция создает словарь для запроса о присутствии клиента"""
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }


def process_ans(message):
    """Функция разбирающая ответ сервера"""
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : Ok!'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    """
    Загрузка параметров из командной строки,
    при их отсутствии - обработка значений, принятых по умолчанию.
    """
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print(
            'В качестве номера порта может быть указано только число в диапазоне 1024-65535.')
        sys.exit(1)

    #  Инициализация сокета и обмен.
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
