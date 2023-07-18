from ward import raises, test

from cachetoolz.coder.decoder import Decoder, register
from cachetoolz.exceptions import RegistryError


@test('register a decoder', tags=['unit', 'decoder', 'register'])
def _():
    decoder = 'test_register'

    def func(arg):
        return arg

    register(func, decoder)

    assert id(Decoder.DECODERS.get(decoder)) == id(func)


@test(
    'register a invalid decoder', tags=['unit', 'decoder', 'register', 'raise']
)
def _():
    error_msg = 'decoder needs to be a callable'

    with raises(RegistryError) as exp:
        register('no callable')

    assert exp.expected_ex_type == RegistryError
    assert exp.raised.args[0] == error_msg
