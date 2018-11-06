import yaml
import inspect

String = ''
Integer = 0
Float = .0
Dict = {}
List = []


class ConfigException(Exception):
    pass


def object_attributes(class_: object) -> List:
    """
    Получить список из (<имя атрибута>, <значение>) явных атрибутов объекта (инстанса или класса).
    Должны вернутся атрибуты (свойства и методы, а также внутренние классы) переданного класса.

    :param class_: Класс, атрибуты которого мы хотим узнать
    :return: List
    """
    def is_magic(name: str):
        return name.startswith('__') and name.endswith('__')

    attributes = inspect.getmembers(class_, lambda attr: not inspect.isroutine(attr))

    return list(filter(lambda attr: not is_magic(attr[0]), attributes))


def object_to_dict_string(obj: object) -> str:
    return '{' + ', '.join(["'{}': {}".format(key, str(value)) for key, value in object_attributes(obj)]) + '}'


def parse_config(model_instance: object, class_: type, data: dict, path: tuple=None) -> object:
    """
    Функция подставляет в инстанс класса модели значения взятые по путям модели из переданных данных.

    :param model_instance: Инстанс класса модели, в который попадут данные
    :param class_: Модель
    :param data: Данные из файла конфига
    :param path: Текущий путь внутри конфига
    :return: Обновленный инстанс model_instance
    """
    if path is None:
        path = (class_.__name__,)

    inspected_keys = set()
    attributes = object_attributes(class_)
    for attr_name, value_or_section in attributes:
        try:
            if isinstance(value_or_section, type):
                value = parse_config(value_or_section(), value_or_section, data[attr_name], path=path + (attr_name,))
            else:
                value = data[attr_name]

            inspected_keys.add(attr_name)
        except KeyError:
            raise ConfigException(f"Can not find key '{attr_name}' at path '{'.'.join(path)}'")  # todo collect errors

        setattr(model_instance, attr_name, value)

    extra_keys = set(data.keys()) - inspected_keys
    if extra_keys:
        raise ConfigException(f"Extra config data found, keys: {extra_keys} (path: {'.'.join(path)})")  # todo collect errors

    return model_instance


class Section:
    """
    Секция внутри AbstractConfig или же Section, позволяет задать иерархию внутри модели конфигурации
    """
    def to_dict(self) -> dict:
        def make_dict(obj) -> dict:
            result = {}
            for key, value in object_attributes(obj):
                if isinstance(value, Section):
                    result[key] = make_dict(value)
                else:
                    result[key] = value

            return result

        return make_dict(self)

    def __str__(self: object):
        return object_to_dict_string(self)


class AbstractConfig(Section):
    """
    Класс для создания своих моделей файлов конфигов.
    Позволяет иметь автодополнение в IDE, вывод типов, а также доступ к атрибутам конфига через точку.

    Для удобства использования метод, загружающий реальный конфиг в инстанс класса мождели вынесен в явный метод,
      что позволяет создать инстанс в модуле, где описана модель, и импортировать этот инстанс отовсюду,
      а инициализировать в нужном месте вашего кода.
    """
    def load(self, path: str) -> None:
        """
        :param path: путь до загружаемого файла конфига
        :return: None
        """
        data = yaml.load(open(path))
        parse_config(self, self.__class__, data)

    def load_from_dict(self, data: dict) -> None:
        parse_config(self, self.__class__, data)
