import argparse
import json
import sys
import socket
import logging
import logs.config_server_log
from errors import IncorrectDataReceivedError, NonDictInputError
from common.variables import *
from common.utils import send_message, get_message
from decor import Log

SERVER_LOGGER = logging.getLogger('server')


@Log(SERVER_LOGGER)
def process_client_message(message, message_list, client):
    """
    Функция-обработчик сообщений от клиентов, принимает словарь-сообщение,
    проверяет корректность, возвращает словарь-ответ для клиента.
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}  # Запрос выполнен успешно.
    return {
        RESPONSE: 400,  # Сервер не смог понять запрос.
        ERROR: 'Bad Request'
    }


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

    # Слушаем порт.
    transport.listen(MAX_CONNECTION)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
            response = process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Сформирован ответ клиенту {response}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} будет закрыто.')
            client.close()
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Не удалось декодировать сообщение от клиента {client_address}. '
                                f'Соединение будет закрыто.')
        except NonDictInputError:
            SERVER_LOGGER.critical(f'Аргумент функции должен быть словарём.')
        except IncorrectDataReceivedError:
            SERVER_LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                                f'Соединение будет закрыто.')
            client.close()


if __name__ == '__main__':
    main()
