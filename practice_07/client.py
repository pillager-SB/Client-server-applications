import argparse
import json
import sys
import time
import socket
from common.variables import *
from common.utils import send_message, get_message
import logging
import logs.config_client_log
from errors import ReqFieldMissingError, NonDictInputError, ServerError
from decor import Log

CLIENT_LOGGER = logging.getLogger('client')


@Log(CLIENT_LOGGER)
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@Log(CLIENT_LOGGER)
def create_message(sock, account_name='Guest'):
    """Функция запрашивает ввод сообщения/команды"""
    message = input('Введите сообщение для отправки\n("exit" - для завершения работы): ')
    match message:
        case 'exit':
            sock.close()
            CLIENT_LOGGER.info('Работа завершена по команде пользователя.')
            sys.exit(0)
        case _:
            message_dict = {
                ACTION: MESSAGE,
                TIME: time.time(),
                ACCOUNT_NAME: account_name,
                MESSAGE_TEXT: message
            }
            CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
            return message_dict


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
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, help='Reading an IP address', nargs='?')
    parser.add_argument('port', type=int, default=DEFAULT_PORT, help='Read port IP address', nargs='?')
    parser.add_argument('-m', '--mode', type=str, default='listen', help='Read clients mode', nargs='?')
    args = parser.parse_args()
    server_address = args.addr
    server_port = args.port
    client_mode = args.mode
    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical(
            f'Номер {server_port} не является приемлемым номером порта. '
            f'Допустимы номера в диапазоне 1024-65535. '
            f'Клиент будет завершен.')
        sys.exit(1)
    if client_mode not in ['listen', 'send']:
        CLIENT_LOGGER.critical(f'{client_mode} - не является допустимым (listen , send) режимом работы.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с параметрами: адрес сервера: {server_address}, '
                       f'порт: {server_port}, режим работы: {client_mode}.')

    #  Инициализация сокета и обмен.
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print('Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error.missing_field}')
        sys.exit(1)
    except NonDictInputError:
        CLIENT_LOGGER.critical(f'Аргумент функции должен быть словарём.')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    except TimeoutError:
        CLIENT_LOGGER.critical(f'Попытка установить соединение была безуспешной, т.к. от '
                               f'{server_address}:{server_port} за требуемое время не получен нужный отклик, '
                               f'или было разорвано уже установленное соединение из-за неверного отклика '
                               f'уже подключенного компьютера')
        sys.exit(1)
    else:
        """Если соединение установлено корректно, начинаю обмен в указанном режиме"""
        print(['Режим работы - приём сообщений.', 'Режим работы - отправка сообщений.'][client_mode == 'send'])
        CLIENT_LOGGER.info(f'Принят ответ: {answer} от сервера {server_address}')

    while True:
        match client_mode:
            case 'send':
                try:
                    send_message(transport, create_message(transport))
                except ConnectionError:
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)
            case 'listen':
                try:
                    message_from_server(get_message(transport))
                except ConnectionError:
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
