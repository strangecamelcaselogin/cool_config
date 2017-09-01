## Cool Config
Простой способ держать конфиг приложения в файле, имея при этом подсветку синтаксиса в IDE.  
Секции могут иметь неограниченную вложенность.

### Использование
Простой пример использования:
```python
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

    print(config)  #  {'b': 42, 'main': {'a': 5}}
    print(config.main.a)  #  5
    print(config.b)  # 42

```
