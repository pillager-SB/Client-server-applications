import argparse
import json
import sys
import time
import socket
from common.variables import *
from common.utils import send_message, get_message
import logging
import logs.config_client_log
from errors import ReqFieldMissingError, NonDictInputError
from decor import Log

CLIENT_LOGGER = logging.getLogger('client')


@Log(CLIENT_LOGGER)
def create_presence(account_name='Guest'):
    """Функция создает словарь для запроса о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@Log(CLIENT_LOGGER)
def process_ans(message):
    """Функция разбирающая ответ сервера"""
    CLIENT_LOGGER.debug(f'Разбор ответа сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : Ok!'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@Log(CLIENT_LOGGER)
def main():
    """
    Загрузка параметров из командной строки,
    при их отсутствии - обработка значений, принятых по умолчанию.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, help='Reading an IP address')
    parser.add_argument('port', type=int, default=DEFAULT_PORT, help='Read port IP address')
    args = parser.parse_args()
    server_address = args.addr
    server_port = args.port
    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical(
            f'Номер {server_port} не является приемлемым номером порта. '
            f'Допустимы номера в диапазоне 1024-65535. '
            f'Клиент будет завершен.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, порт: {server_port}.')

    #  Инициализация сокета и обмен.
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))

    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error.missing_field}')
    except NonDictInputError:
        CLIENT_LOGGER.critical(f'Аргумент функции должен быть словарём.')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')
    except TimeoutError:
        CLIENT_LOGGER.critical(f'Попытка установить соединение была безуспешной, т.к. от '
                               f'{server_address}:{server_port} за требуемое время не получен нужный отклик, '
                               f'или было разорвано уже установленное соединение из-за неверного отклика '
                               f'уже подключенного компьютера')
    else:
        CLIENT_LOGGER.info(f'Принят ответ: {answer} от сервера {server_address}')


if __name__ == '__main__':
    main()
