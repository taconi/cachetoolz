from dataclasses import dataclass

from ward import each, raises, test

from cachetoolz.coder.encoder import encode, register
from cachetoolz.exceptions import RegistryError, UnknownEncoderError


@dataclass
class ColorHex:
    name: str
    code: str


@dataclass
class ColorRGB:
    name: str
    code: str


@test('encode not implemented', tags=['unit', 'encoder', 'raise'])
def _():
    value = ColorHex(name='pink', code='ff748c')
    error_msg = f'Encoder not implemented {value=} type {type(value)}'

    with raises(UnknownEncoderError) as exp:
        encode(value)

    assert exp.expected_ex_type == UnknownEncoderError
    assert exp.raised.args[0] == error_msg


@test('register encoder', tags=['unit', 'encoder', 'register'])
def _():
    @register
    def func(value: ColorRGB):
        return value.value

    assert encode.registry.get(ColorRGB)


@test(
    'register encoder invalid', tags=['unit', 'encoder', 'register', 'raise']
)
def _(
    func=each('not callable', lambda value: None),
    error_msg=each(
        'encoder needs to be a callable',
        'encoder needs to have a parameter named `value` '
        'and it needs to have the type annotated',
    ),
):
    with raises(RegistryError) as exp:
        register(func)

    assert exp.expected_ex_type == RegistryError
    assert exp.raised.args[0] == error_msg
