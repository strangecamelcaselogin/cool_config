## Cool Config
Simple way to use configuration files with Python configuration model.

## Requires

Python 3.6+

### Usage
Simple usage example:

```python

from cool_config import *


class Config(AbstractConfig):
    """
    Configuration model inherits from AbstractConfig, and all configuration sections from Section
    """
    class main(Section):
        a = Integer

    b = Integer


config = Config()  # create global configuration object and import it


# more examples available in test/main.py
if __name__ == '__main__':
    config_data = {
        'main': {
            'a': 5
        },
        'b': 42
    }

    # config.load('config.yml')  # initialize configuration with config.yml in 
    #   you application entry point (before `config` usage)
    config.update_from_dict(config_data)
    

    print(config)  # {'b': 42, 'main': {'a': 5}}
    print(config.main.a)  # 5
    print(config.b)  # 42

    config_data_b = {
        'main': {
            'a': 55
        },
    }
    config.update_from_dict(config_data_b)
    print(config)  # {'b': 42, 'main': {'a': 55}}

    """
    ENVIRONMENT:
        TEST__main__a = '6'
        TEST__b = '22'
        THE_ANSWER_KEY = '42'
    """
    config.update_from_env('TEST', delimiter='__')
    print(config)  # {'b': '22', 'main': {'a': '6'}}

```