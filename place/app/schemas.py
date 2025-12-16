import attrs


# TODO: validators
@attrs.define(frozen=True)
class RGBColor:
    r: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    g: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    b: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))

    @property
    def tuple(self):
        return (self.r, self.g, self.b)


# TODO: validators
@attrs.define(frozen=True)
class Pixel:
    x: int
    y: int
    color: RGBColor


# TODO: validators
@attrs.define(frozen=True)
class RGBAColor:
    r: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    g: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    b: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))
    a: int = attrs.field(validator=(attrs.validators.ge(0), attrs.validators.lt(256)))

    @property
    def tuple(self):
        return (self.r, self.g, self.b, self.a)


# TODO: validators
@attrs.define(frozen=True)
class CanvasConfig:
    height: int = attrs.field(
        validator=(attrs.validators.ge(200), attrs.validators.le(1000))
    )
    width: int = attrs.field(
        validator=(attrs.validators.ge(200), attrs.validators.le(1000))
    )
    background_color: RGBAColor
