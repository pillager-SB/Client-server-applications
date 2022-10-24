import argparse
import json
import sys
import socket
import select
import time
import logging
import logs.config_server_log
from common.variables import *
from common.utils import send_message, get_message
from decor import Log

SERVER_LOGGER = logging.getLogger('server')


@Log(SERVER_LOGGER)
def process_client_message(message, messages_list, client):
    """
    Функция-обработчик сообщений от клиентов, принимает словарь-сообщение,
    проверяет корректность, возвращает словарь-ответ для клиента.
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})  # Если правильное сообщение о присутствии, принимаем и отвечаем.
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))  # Если это сообщение,
        # ставим его в очередь сообщений.
    else:
        send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})  # Отправляем сообщение о том,
        # что сервер не смог понять запрос.


@Log(SERVER_LOGGER)
def main():
    """
    Загрузка параметров из командной строки,
    при их отсутствии - обработка значений, принятых по умолчанию.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default='', help='Reading an IP address', nargs='?')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, help='Read port IP address', nargs='?')
    args = parser.parse_args()
    listen_address = args.addr
    listen_port = args.port

    # Проверка получения корректного номера порта для работы сервера.
    if listen_port < 1024 or listen_port > 65535:
        SERVER_LOGGER.critical(
            f'Номер {listen_port} не является приемлемым номером порта. '
            f'Допустимы номера в диапазоне 1024-65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

    # Готовим сокет.
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    #  Списки:
    clients = []  # Список клиентов.
    messages = []  # Список очереди сообщений.

    # Слушаем порт.
    transport.listen(MAX_CONNECTION)

    while True:
        #  Ожидаю подключения, если timeout пройден, безопасно ловлю исключение.
        try:
            client, client_address = transport.accept()
        except OSError as err:
            print(err.errno)
            ...
        else:
            SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
            clients.append(client)
        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяю, есть ли клиенты в списке.
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            ...
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
