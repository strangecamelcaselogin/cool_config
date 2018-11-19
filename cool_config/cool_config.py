import os
import inspect
from pprint import pformat
from typing import Tuple

import yaml


String = ''
Integer = 0
Float = .0
Dict = {}
List = []


class ConfigException(Exception):
    pass


def env_to_path(var_name: str, delimiter: str) -> Tuple[str]:
    path = var_name.split(delimiter)
    path.pop(0)
    if path:
        return tuple(map(lambda k: str(k), filter(lambda p: p != '', path)))


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

    def parse(self, model_instance: object, class_: type, data: dict, allow_to_fail, path: tuple=None) -> object:
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


class Section:
    """
    Configuration section, for hierarchy support
    """
    def to_dict(self) -> dict:
        def make_dict(obj) -> dict:
            result = {}
            for key, value in ConfigParser.object_attributes(obj):
                if isinstance(value, Section):
                    result[key] = make_dict(value)
                else:
                    result[key] = value

            return result

        return make_dict(self)

    def _get(self, path):
        o = self
        for p in path:
            o = getattr(o, p)

        return o

    def _set(self, path, value):
        parent = None
        o = self
        for p in path:
            parent = o
            o = getattr(o, p)

        if parent:
            setattr(parent, path[-1], value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self):
        return pformat(self.to_dict(), indent=4)


class AbstractConfig(Section):
    """
    Abstract configuration model class. Must be inherited with you configuration model
    """
    def __load(self, data: dict, allow_to_fail=False) -> 'AbstractConfig':
        ConfigParser().parse(self, self.__class__, data, allow_to_fail)

        return self

    def load(self, path: str):
        """
        Basic method to load yaml formatted files as configuration data
        :param path: path to file
        """
        with open(path) as f:
            return self.__load(yaml.load(f))

    def update_from_dict(self, data: dict, allow_missing_keys=True) -> 'AbstractConfig':
        """
        Update configuration model with dictionary data
        :param data: dictionary data
        :param allow_missing_keys: allowing to update config partially
        """
        return self.__load(data, allow_to_fail=allow_missing_keys)

    def update_from_file(self, path: str, allow_missing_keys=True) -> 'AbstractConfig':
        """
        Update configuration model with (another) configuration file
        :param path: path to file
        :param allow_missing_keys: allowing to update config partially
        """
        with open(path) as f:
            return self.__load(yaml.load(f), allow_to_fail=allow_missing_keys)

    def update_from_env(self, env_prefix: str, delimiter: str='__') -> 'AbstractConfig':
        """
        Update configuration instance state with environment variables.
        For example, let be prefix = 'TEST', delimiter = '__', and environment variables:
            TEST__section1__variable
            TEST__section1__section2__variable
            TEST__section1__variable_name_with_underline

        With this variables method will update section1.variable, section1.section2.variable and
          section1.variable_name_with_underline.

        :param env_prefix: variable prefix
        :param delimiter: delimiter of sections path
        """
        environ = os.environ

        suitable_keys = filter(lambda k: k.startswith(env_prefix + delimiter), environ.keys())
        for key in suitable_keys:
            path = env_to_path(key, delimiter)
            if path is None:
                raise ConfigException(f'Incorrect environment variable ({key}) format with prefix {env_prefix}')

            try:
                self._set(path, environ[key])
            except AttributeError:
                raise ConfigException(f'Can not update self with environment variable "{key}"')

        return self
