import os


class ConvertError(ValueError):

    def __init__(self, *args, **kwargs):
        super(ConvertError, self).__init__(*args)
        self.name = kwargs.pop("name")
        self.raw_value = kwargs.pop("raw_value")
        self.expected_type = kwargs.pop("expected_type")

    def as_dict(self):
        return {
            "field": self.name,
            "value": self.raw_value,
            "expected_type": self.expected_type,
        }


class ValueRequired(ValueError):
    def __init__(self, *args, **kwargs):
        super(ValueRequired, self).__init__(*args)
        self.name = kwargs.pop("name")

    def as_dict(self):
        return {
            "field": self.name,
            "required": True,
        }


class NotInited(object):
    pass


class BaseField(object):

    type_name = "abstract_type"

    def __init__(self, name, default=None, required=False):
        self.name = name
        self.default = default
        self._required = required
        self._cached_value = NotInited()

    def raise_error(self, value):
        raise ConvertError(
            "Error: environ %s=%s is not of type %s"
            % (self.name, self._cached_value, self.type_name),
            name=self.name,
            raw_value=value,
            expected_type=self.type_name,
        )

    def _get_value(self):
        value = os.environ.get(self.name)
        if value is not None:
            return self.convert(value)
        else:
            if self._required:
                raise ValueRequired(
                    "Value of environ %s is required.",
                    name=self.name,
                )
        return self.default

    @property
    def value(self):
        if isinstance(self._cached_value, NotInited):
            self.update()
        return self._cached_value

    def update(self):
        value = self._get_value()
        self._cached_value = value
        return value

    def convert(self, value):
        return value


class StringField(BaseField):

    type_name = "string"


class IntField(BaseField):

    type_name = "integer"

    def convert(self, value):
        try:
            return int(value)
        except ValueError:
            self.raise_error(value)


class FloatField(BaseField):

    type_name = "float"

    def convert(self, value):
        try:
            return float(value)
        except ValueError:
            self.raise_error(value)


class BooleanField(BaseField):

    type_name = "boolean"

    _true_set = {"true"}
    _false_set = {"false"}

    def convert(self, value):
        _value = value.lower()
        if _value in self._true_set:
            return True
        elif _value in self._false_set:
            return False
        else:
            self.raise_error(value)


class EnvModel(object):

    def __init__(self):
        self._fields = [
            field_name for field_name in dir(self.__class__)
            if isinstance(getattr(self.__class__, field_name), BaseField)
        ]
        self.errors = []
        self._build_data()

    def _build_data(self):
        self.errors = []
        for field in self._fields:
            try:
                getattr(self.__class__, field).update()
            except (ConvertError, ValueRequired) as e:
                self.errors.append(e.as_dict())

    def is_valid(self):
        return len(self.errors) <= 0

    def update(self):
        """
        Update values from env again.
        """
        self._build_data()
