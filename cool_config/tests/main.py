from unittest import TestCase, mock
import yaml
from cool_config import AbstractConfig, Section, Integer, Boolean, String


class Config(AbstractConfig):
    class main(Section):
        a = Integer

    b = Integer
    c = Boolean
    d = Boolean
    e = String


base_data = {
    'main': {
        'a': 5
    },
    'b': 42,
    'c': True,
    'd': False,
    'e': 'test'
}


class TestLoading(TestCase):
    def test_file_load(self):
        test_fake_file = 'test.yml'
        yml = yaml.dump(base_data)
        with mock.patch('cool_config.cool_config.open', new=mock.mock_open(read_data=yml)) as m:
            config = Config()

            config.load(test_fake_file)

            self.assertDictEqual(base_data, config.to_dict())
            m.assert_called_once_with(test_fake_file)

            return config

    def test_dict_load_and_update(self):
        config = Config()
        config.update_from_dict(base_data)

        self.assertDictEqual(base_data, config.to_dict())

        update_data = {
            'main': {
                'a': 111
            }
        }

        config.update_from_dict(update_data)

        updated_data = {**base_data, **update_data}
        self.assertDictEqual(updated_data, config.to_dict())

    def test_file_load_and_file_update(self):
        config = self.test_file_load()
        self.assertDictEqual(base_data, config.to_dict())

        update_data = {
            'main': {
                'a': 111
            }
        }
        test_fake_file = 'test.yml'
        yml = yaml.dump(update_data)
        with mock.patch('cool_config.cool_config.open', new=mock.mock_open(read_data=yml)) as m:

            config.update_from_file(test_fake_file)

            combined_data = {}
            combined_data.update(base_data)
            combined_data.update(update_data)

            self.assertDictEqual(combined_data, config.to_dict())
            m.assert_called_once_with(test_fake_file)

    def test_file_load_and_env_update(self):
        config = self.test_file_load()
        self.assertDictEqual(base_data, config.to_dict())

        env = {
            'TEST__main__a': '6',
            'TEST__b': '22',
            'TEST__c': 'False',
            'TEST__d': 'True',
            'TEST__e': 'true',
            'THE_ANSWER_KEY': '42'
        }

        env_updated = {**base_data, **{
            'main': {
                'a': 6
            },
            'b': 22,
            'c': False,
            'd': True,
            'e': 'true'
        }}

        with mock.patch.dict('os.environ', env):
            config.update_from_env('TEST', delimiter='__')

            self.assertDictEqual(env_updated, config.to_dict())
