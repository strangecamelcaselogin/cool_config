from cool_config import *


class Config(AbstractConfig):
    """
    Модель конфига, сам конфиг наследуется от AbstractConfig, а все секции от Section.
    """
    class main(Section):
        a = Integer

    b = Integer


config = Config()  # создадим глобальный объект, который легко импортировать из любого другого модуля

if __name__ == '__main__':
    config.load('config.yml')  # проинициализируем его там, где это необходимо

    print(config)
    print(config.main.a)
    print(config.b)
