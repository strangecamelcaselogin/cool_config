import inspect
from typing import List

from cool_config.exceptions import ConfigException


class ConfigParser:
    @staticmethod
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

    def parse(self, model_instance: object, class_: type, data: dict, allow_to_fail, path: tuple = None) -> object:
        """
        Функция подставляет в инстанс класса модели значения взятые по путям модели из переданных данных.

        :param model_instance: Инстанс класса модели, в который попадут данные
        :param class_: Модель
        :param data: Данные из файла конфига
        :param allow_to_fail: Позволяет проигнорировать ошибки нехватки данных, используется для обновления модели из файла/словаря
        :param path: Текущий путь внутри конфига
        :return: Обновленный инстанс model_instance
        """
        if path is None:
            path = (class_.__name__,)

        inspected_keys = set()
        attributes = self.object_attributes(class_)
        for attr_name, value_or_section in attributes:
            try:
                if isinstance(value_or_section, type):
                    value = self.parse(value_or_section(), value_or_section, data[attr_name], allow_to_fail=allow_to_fail, path=path + (attr_name,))
                else:
                    value = data[attr_name]

                inspected_keys.add(attr_name)
            except KeyError:
                if not allow_to_fail:
                    raise ConfigException(f"Can not find key '{attr_name}' at path '{'.'.join(path)}'")  # todo collect errors

            else:
                setattr(model_instance, attr_name, value)

        extra_keys = set(data.keys()) - inspected_keys
        if extra_keys:
            raise ConfigException(f"Extra config data found, keys: {extra_keys} (path: {'.'.join(path)})")  # todo collect errors

        return model_instance
