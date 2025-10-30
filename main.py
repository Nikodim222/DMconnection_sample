"""
* Соединение к серверу DMconnect
* *************************
* Пример простейшего соединения к серверу DMconnect.
* См. также клиент "dsconnect": http://dsconnect.narod.ws
* Программа является кроссплатформенной. Она должна работать
* под Microsoft Windows, Linux, macOS и т.д.
*
* @author Ефремов А. В., 30.10.2025
"""

from typing import Optional, List, NamedTuple
import configparser
from time import sleep

from dmconn import DMconn # подключение класса для работы с протоколом DMconnect
from miscellaneous import Miscellaneous
from models import Constant

class ConfigType(NamedTuple):
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]
    join_server: Optional[str]
    messages: List[str]

def get_config() -> ConfigType:
    """
    * Получение конфигурации программы
    """
    CONNECTION_SECTION: str = "connection"
    P_HOST: str = "host"
    P_PORT: str = "port"
    P_USER: str = "user"
    P_PASSWORD: str = "password"
    P_JOIN_SERVER: str = "join_server"
    MESSAGES_SECTION = "messages"
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    join_server: Optional[str] = None
    messages: List[str] = []
    if Miscellaneous.is_file_readable(Constant.SETTINGS_FILE.value):
        config = configparser.ConfigParser()
        try:
            with open(Constant.SETTINGS_FILE.value, 'r', encoding=Constant.GLOBAL_CODEPAGE.value) as f:
                config.read_file(f)
                if CONNECTION_SECTION in config:
                    if P_HOST in config[CONNECTION_SECTION]:
                        host = config[CONNECTION_SECTION][P_HOST].strip()
                    if P_PORT in config[CONNECTION_SECTION]:
                        port = config.getint(CONNECTION_SECTION, P_PORT)
                        if not (1 <= port <= 65534):
                            raise ValueError("Значение порта вне допустимого диапазона (1 - 65534)")
                    if P_USER in config[CONNECTION_SECTION]:
                        user = config[CONNECTION_SECTION][P_USER].strip()
                    if P_PASSWORD in config[CONNECTION_SECTION]:
                        password = config[CONNECTION_SECTION][P_PASSWORD]
                    if P_JOIN_SERVER in config[CONNECTION_SECTION]:
                        join_server = config[CONNECTION_SECTION][P_JOIN_SERVER].strip()
                if MESSAGES_SECTION in config:
                    for p_messages in config[MESSAGES_SECTION]:
                        msg: str = config[MESSAGES_SECTION][p_messages]
                        if msg is not None and not "".__eq__(msg):
                            messages.append(msg)
        except FileNotFoundError:
            Miscellaneous.print_message(f"Ошибка: Файл настроек не найден: {Constant.SETTINGS_FILE.value}")
            raise
        except ValueError:
            Miscellaneous.print_message("Значение параметра не соответствует типу данных в конфигурационном файле.")
            raise
        except Exception as e:
            Miscellaneous.print_message(f"Ошибка при чтении файла настроек: {e}")
            raise
    return ConfigType(host, port, user, password, join_server, messages)

def main() -> None:
    conf: ConfigType = get_config()
    if conf.host is not None and conf.port is not None and conf.user is not None and conf.password is not None and conf.join_server is not None:
        Miscellaneous.print_message("Подключение к серверу...")
        dm_obj: DMconn = DMconn(conf.host, conf.port, conf.user, conf.password, conf.join_server)
        if dm_obj.sock is not None:
            Miscellaneous.print_message("Подключено.")
            if len(conf.messages) > 0:
                for msg in conf.messages:
                    dm_obj.write(msg)
                    print(msg)
                    sleep(5)
            if len(dm_obj.msg_buffer) > 0:
                Miscellaneous.print_message("Пришёл ответ от сервера (см. ниже).")
                for line in dm_obj.msg_buffer:
                    print(line)
            else:
                Miscellaneous.print_message("От сервера никакого ответа не пришло.")
            Miscellaneous.print_message("Закрытие соединения с сервером...")
            dm_obj.close()
            Miscellaneous.print_message("Соединение разорвано.")
        else:
            Miscellaneous.print_message("Отсутствует подключение к серверу.")
    else:
        Miscellaneous.print_message("Необходимая конфигурация программы не определена.")
    Miscellaneous.print_message("Завершение работы программы.")

# Точка запуска программы
if __name__ == "__main__":
    main()
