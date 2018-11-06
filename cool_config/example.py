from cool_config import *


class Config(AbstractConfig):
    """
    Configuration model inherits from AbstractConfig, and all configuration sections from Section
    """
    class main(Section):
        a = Integer

    b = Integer


config = Config()


if __name__ == '__main__':
    config_data = {
        'main': {
            'a': 5
        },
        'b': 42
    }

    config.load_from_dict(config_data)

    print(config.main.a)
    print(config.b)
