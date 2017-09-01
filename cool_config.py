import yaml
import inspect

String = ''
Integer = 0
Float = .0
Dict = {}
List = []

__all__ = ['AbstractConfig', 'Section', 'String', 'Integer', 'Float', 'Dict', 'List']


def object_attributes(class_: object) -> List:
    """
    Получить список из (<имя атрибута>, <значение>) явных атрибутов объекта (инстанса или класса).
    Должны вернутся атрибуты (свойства и методы, а также внутренние классы) переданного класса.

    :param class_: Класс, атрибуты которого мы хотим узнать
    :return: List
    """
    attributes = inspect.getmembers(class_, lambda a: not (inspect.isroutine(a)))
    return list(filter(lambda a: not (a[0].startswith('__') and a[0].endswith('__')), attributes))


def object_to_dict_string(obj: object) -> str:
    """
    :param obj: Объект
    :return: str
    """
    return '{' + ', '.join(["'{}': {}".format(key, str(value)) for key, value in object_attributes(obj)]) + '}'


def parse_config(instance: object, class_: type, data: dict) -> object:
    """
    Функция подставляет в инстанс класса модели значения взятые по путям модели из переданных данных.

    :param instance: Инстанс класса модели, в который попадут данные
    :param class_: Модель
    :param data: Данные из файла конфига
    :return: обновленный инстанс
    """
    for key, value in object_attributes(class_):
        setattr(instance, key, parse_config(value(), value, data[key]) if isinstance(value, type) else data[key])

    return instance


class Section:
    """
    Позволяет вывести секцию с помощью print.
    """
    def to_dict(self) -> dict:
        """
        Дамп конфига в dict.
        :return: dict
        """
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
