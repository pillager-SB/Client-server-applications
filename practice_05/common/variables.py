"""Constants"""
import logging

# Порт по умолчанию для сетевого взаимодействия.
DEFAULT_PORT = 7777
# IP-адрес по умолчанию для подключения клиента.
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Max размер очереди подключений.
MAX_CONNECTION = 5
# Max длина сообщения в байтах.
MAX_PACKAGE_LENGTH = 1024
# Используемая в проекте кодировка.
ENCODING = 'utf-8'
# Установка для верхнего уровня логирования.
LOGGING_LEVEL = logging.DEBUG


# Основные ключи протокола JIM.
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Прочие ключи используемые в протоколе.
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
