## Cool Config
Simple way to use configuration files with Python configuration model.

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


config = Config()  # global cpnfiguration object


if __name__ == '__main__':
    config_data = {
        'main': {
            'a': 5
        },
        'b': 42
    }

    config.load_from_dict(config_data) # initialize configuration from dict 
    # config.load('config.yml')  # or initialize configuration with config.yml

    print(config.main.a)  #  5
    print(config.b)  # 42

```
