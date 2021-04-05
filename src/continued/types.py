#!/usr/bin/env python3

from typing import (
    AbstractSet as _AbstractSet,
    Any as _Any,
    ByteString as _ByteString,
    Callable as _Callable,
    Collection as _Collection,
    Container as _Container,
    Dict as _Dict,
    Iterable as _Iterable,
    Iterator as _Iterator,
    List as _List,
    Mapping as _Mapping,
    MutableMapping as _MutableMapping,
    MutableSequence as _MutableSequence,
    MutableSet as _MutableSet,
    Optional as _Optional,
    Sequence as _Sequence,
    Text as _Text,
    Tuple as _Tuple,
    Type as _Type,
    TypeVar as _TypeVar,
    Union as _Union,

    get_origin as _get_origin,
)

from collections.abc import (
    ItemsView as _ItemsView,
    KeysView as _KeysView,
    ValuesView as _ValuesView,
)

from numbers import (
    Integral as _Integral,
    Real as _Real,
)

import sys as _sys

from collections import namedtuple as _namedtuple
from copy import deepcopy as _deepcopy

import pendulum as _pendulum

from pendulum.parsing import parse_iso8601 as _parse_iso8601


# A singleton distinct from None, so both absence of an argument
# as well as an explicit None argument can be easily represented.
ABSENT = type(
    'AbsentType', (type,), {'__bool__': bool, '__hash__': None,
                            '__module__': None, '__repr__': lambda _: 'ABSENT'}
)(
    'ABSENT', (), {'__module__': None, '__new__': None}
)
type(ABSENT).__new__ = lambda _: ABSENT
type(ABSENT).__init__ = lambda _: None


Coords = _namedtuple('Coords', 'x y z')


class L(str):

    class localised:

        def __get__(self, instance, owner=None) -> str:

            return instance.__dict__['localised']

        def __set__(self, instance, value) -> None:

            raise AttributeError("attribute localised is read-only")

    localised = localised()

    def __new__(cls, s: _Union[str, 'L'] = ABSENT, /,
                localised: _Optional[str] = ABSENT) -> 'L':

        if isinstance(s, L) and localised is ABSENT:
            return s

        obj = super().__new__(cls) if s is ABSENT else super().__new__(cls, s)

        if localised not in (ABSENT, None):
            obj.__dict__['localised'] = str(localised)

        else:
            obj.__dict__['localised'] = str(obj)

        return obj

    def __repr__(self) -> str:

        s = str(self)
        localised = self.__dict__['localised']
        if localised == s:
            return f"{type(self).__name__}({s!r})"

        return f"{type(self).__name__}({s!r}, {localised!r})"


class DateTime(_pendulum.DateTime):

    @classmethod
    def from_elite_string(cls, timestamp: str, tz=None) -> 'DateTime':

        dt = _parse_iso8601(timestamp)
        dt = _pendulum.instance(dt, tz=_pendulum.local_timezone())
        dt = dt.in_timezone(tz)

        assert dt.microsecond == 0
        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second,
                   tzinfo=dt.tzinfo, fold=dt.fold)

    def to_elite_string(self) -> str:

        dt = self.in_timezone(_pendulum.UTC)
        dt = dt.replace(microsecond=0)
        timestamp = dt.to_iso8601_string()

        return timestamp

    @classmethod
    def now(cls, tz=None) -> 'DateTime':

        dt = _pendulum.now(tz)

        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second, dt.microsecond,
                   tzinfo=dt.tzinfo, fold=dt.fold)

    @classmethod
    def utcnow(cls) -> 'DateTime':

        dt = _pendulum.now(_pendulum.UTC)

        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second, dt.microsecond,
                   tzinfo=dt.tzinfo, fold=dt.fold)

    @classmethod
    def today(cls) -> 'DateTime':

        dt = _pendulum.now()

        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second, dt.microsecond,
                   tzinfo=dt.tzinfo, fold=dt.fold)

    @classmethod
    def fromtimestamp(cls, t, tz=None) -> 'DateTime':

        dt = _pendulum.from_timestamp(t, tz)

        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second, dt.microsecond,
                   tzinfo=dt.tzinfo, fold=dt.fold)

    @classmethod
    def utcfromtimestamp(cls, t) -> 'DateTime':

        dt = _pendulum.from_timestamp(t)

        return cls(dt.year, dt.month, dt.day,
                   dt.hour, dt.minute, dt.second, dt.microsecond,
                   tzinfo=dt.tzinfo, fold=dt.fold)


_REVERT_MARKER = object()
_D = _TypeVar('_D')


class Data(_Mapping):

    _attrs: _Dict[str, 'Attr'] = {}
    _key_map: _Dict[str, 'Attr'] = {}

    _data: _Dict[str, _Any]
    _unknown: _Dict[str, _Any]

    @classmethod
    def __init_subclass__(cls, **kwargs) -> None:

        super().__init_subclass__(**kwargs)

        attrs = cls._attrs = {}
        key_map = cls._key_map = {}

        for base in reversed(cls.__bases__):
            attrs.update(base.__dict__['_attrs'])
            key_map.update(base.__dict__['_key_map'])

        for attr in cls.__dict__.values():
            if not isinstance(attr, Attr):
                continue

            attrs[attr.name] = attr

            if attr.delegate:
                key_map.update((k, attr) for k in attr.key)
            else:
                key_map[attr.key] = attr

    def __init__(self, _unknown=None, **kwargs) -> None:

        self._data = {}
        self._unknown = {} if not _unknown else dict(_unknown)

        for name, attr in self._attrs.items():

            try:
                # attr.param == None will also trigger a KeyError
                # and consequently end up with the default value.
                value = kwargs.pop(attr.param)

            except KeyError:
                value = attr.default_factory()

            else:
                if not isinstance(value, attr.type):
                    if attr.precheck and not attr.precheck(value):
                        raise ValueError(
                            f"invalid value {value!r} for attribute {attr.param}"
                        )

                    if attr.convert:
                        value = attr.convert(value)

                    else:  # Already holds: if not isinstance(value, attr.type)
                        value = attr.type(value)

                if attr.validate and not attr.validate(value):
                    raise ValueError(
                        f"invalid value {value!r} for attribute {attr.param}"
                    )

            if value is not None:
                self._data[attr.name] = value
            elif attr.delegate and not issubclass(attr.type, L):
                self._data[attr.name] = attr.type()

        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls: _Type[_D], data: _Mapping[str, _Any], copy=True) -> _D:

        obj = super().__new__(cls)
        obj._data = {}

        if copy or not isinstance(data, _MutableMapping):
            data = _deepcopy(data)

        for name, attr in cls._attrs.items():

            if attr.delegate:

                if issubclass(attr.type, L):

                    value = [data.pop(k, None) for k in attr.key]
                    if value[0] is None:
                        value = attr.default_factory()

                    else:
                        value = cls._init_entry(attr, value)

                else:
                    value = {}
                    for key in attr.key:
                        try:
                            value[key] = data.pop(key)
                        except KeyError:
                            pass

                    value = cls._init_entry(attr, value)

            else:
                try:
                    value = data.pop(attr.key)

                except KeyError:
                    value = attr.default_factory()

                else:
                    value = cls._init_entry(attr, value)

            if value is not None:
                obj._data[attr.name] = value

        obj._unknown = data
        return obj

    @staticmethod
    def _init_entry(attr: 'Attr', value: _Any) -> _Any:

        if attr.precheck and not attr.precheck(value):
            raise ValueError(
                f"invalid value {value!r} for member {attr.key}"
            )

        # FIXME: make L a delegate

        if attr.convert:
            value = attr.convert(value)

        elif not isinstance(value, attr.type):
            value = attr.type(value)

        if attr.validate and not attr.validate(value):
            raise ValueError(
                f"invalid value {value!r} for member {attr.key}"
            )

        return value

    def __repr__(self) -> str:

        args = []

        for name, attr in self._attrs.items():
            if attr.param is None:
                continue

            value = self._data.get(name)
            if value == attr.default_factory():
                continue

            args += [f"{attr.param}={value!r}"]

        if self._unknown:
            args += [f"_unknown={self._unknown!r}"]

        return f"{type(self).__name__}({', '.join(args)})"

    def __bool__(self) -> bool:

        return bool(len(self._data))

    def __len__(self) -> int:

        return sum(
            (2 if isinstance(value, L) else len(value))
            if self._attrs[name].delegate else 1
            for name, value in self._data.items()
        ) + len(self._unknown)

    def __contains__(self, key) -> bool:

        try:
            attr = self._key_map[key]

        except KeyError:
            return key in self._unknown

        if attr.delegate and not issubclass(attr.type, L):
            return key in self._data[attr.name]

        return attr.name in self._data

    def __getitem__(self, key) -> _Any:

        try:
            attr = self._key_map[key]

        except KeyError:
            return self._unknown[key]

        if attr.delegate:
            if not issubclass(attr.type, L):
                return self._data[attr.name][key]

            value = self._data[attr.name]
            return value.localised if key.endswith('_Localised') else str(value)

        value = self._data[attr.name]
        return (attr.revert(value, {id(_REVERT_MARKER): _REVERT_MARKER})
                if attr.revert else value)

    def __iter__(self) -> _Iterator[str]:

        for name, value in self._data.items():
            attr = self._attrs[name]

            if attr.delegate:
                if not issubclass(attr.type, L):
                    yield from value
                else:
                    yield from attr.key
                continue

            yield attr.key

        yield from self._unknown.keys()

    def __iteritems__(self) -> _Iterator[_Tuple[str, _Any]]:

        for name, value in self._data.items():
            attr = self._attrs[name]

            if attr.delegate:
                if not issubclass(attr.type, L):
                    yield from value.__iteritems__()
                else:
                    yield from zip(attr.key, (str(value), value.localised))
                continue

            yield (attr.key,
                   attr.revert(value, {id(_REVERT_MARKER): _REVERT_MARKER})
                   if attr.revert else value)

        yield from self._unknown.items()

    def keys(self) -> _KeysView:

        class KeysView(_KeysView):
            def __init__(self, data: Data) -> None:
                super().__init__(data)

                self.__iter__ = data.__iter__
                self.__len__ = data.__len__

        return KeysView(self)

    def items(self) -> _ItemsView:

        class ItemsView(_ItemsView):
            def __init__(self, data: Data) -> None:
                super().__init__(data)

                self.__iter__ = data.__iteritems__
                self.__len__ = data.__len__

        return ItemsView(self)

    def values(self) -> _ValuesView:

        class ValuesView(_ValuesView):
            def __init__(self, data: Data) -> None:
                super().__init__(data)

                self.__iter__ = lambda: (v for _, v in data.__iteritems__())
                self.__len__ = data.__len__

        return ValuesView(self)

    def __deepcopy__(self, memo) -> _Any:

        if id(_REVERT_MARKER) in memo:

            d = {}
            memo[id(self)] = d

            for name, value in self._data.items():
                attr = self._attrs[name]

                if attr.revert:
                    value = attr.revert(value,
                                        {id(_REVERT_MARKER): _REVERT_MARKER})

                if attr.delegate:
                    if not issubclass(attr.type, L):
                        d.update(value)
                    else:
                        key1, key2 = attr.key
                        d[key1] = str(value)
                        d[key1] = value.localised
                else:
                    d[attr.key] = value

            d.update(self._unknown)
            return d

        obj = super().__new__(type(self))
        memo[id(self)] = obj
        obj._data = {k: _deepcopy(v, memo) for k, v in self._data}
        obj._unknown = {k: _deepcopy(v, memo) for k, v in self._unknown}
        return obj

    def __copy__(self) -> 'Data':

        obj = super().__new__(type(self))
        obj._data = self._data.copy()
        obj._unknown = self._unknown.copy()
        return obj


class Attr:

    def __init__(
            self, *,
            name: str = ABSENT,
            type_: _Type = ABSENT,
            key: _Union[str, _Collection[str]] = ABSENT,
            param: _Optional[str] = ABSENT,
            default: _Any = ABSENT,
            default_factory: _Callable[[], _Any] = ABSENT,
            precheck: _Callable[[_Any], bool] = ABSENT,
            convert: _Callable[[_Any], _Any] = ABSENT,
            validate: _Callable[[_Any], bool] = ABSENT,
            revert: _Callable[[_Any, _Dict], _Any] = ABSENT,
    ) -> None:

        self.name = name
        self.type = type_
        self.key = key
        self.param = param

        if default is ABSENT:
            self.default_factory = default_factory
        elif default_factory:
            raise ValueError("cannot have both default and default_factory")
        else:
            self.default_factory = lambda: default

        self.precheck = precheck
        self.convert = convert
        self.validate = validate
        self.revert = revert

        if name is not ABSENT:
            if type_ is ABSENT:
                raise TypeError("must also specify type when specifying name")

            self._fill_funcs_from_type()

    def __get__(self, instance: Data, owner: _Type[Data] = None) -> _Any:

        return instance._data[self.name]

    def __set__(self, instance: Data, value: _Any) -> None:

        raise AttributeError("attribute is read-only")

    def __set_name__(self, owner: _Type[Data], name: str) -> None:

        self.name = name

        if self.key is ABSENT:
            self.key = _py2key(name)

        if self.param is ABSENT:
            self.param = name if not name.startswith('_') else None

        if self.type is ABSENT:
            try:
                anno = owner.__annotations__[name]
            except (AttributeError, KeyError):
                raise TypeError("attribute needs type annotation") from None
            else:
                self.type = (
                    anno if not isinstance(anno, str)
                    else eval(anno, _sys.modules[owner.__module__].__dict__, {})
                )

        self._fill_funcs_from_type()

    # noinspection PyUnboundLocalVariable
    def _fill_funcs_from_type(self) -> None:
        typ = _get_origin(self.type) or self.type
        is_concrete = type(self.type) is type

        for abstract, concrete, precheck, revert in _FUNC_DEFAULT_MATRIX:
            if issubclass(typ, abstract):
                break

        if issubclass(typ, L):
            self.delegate = True
            self.key = (self.key, self.key + '_Localised')

        elif not isinstance(self.key, str) and isinstance(self.key, _Collection):
            self.delegate = True
            if self.key:
                self.key = tuple(self.key)
            else:
                self.key = tuple(self.type._key_map)

        else:
            self.delegate = False

        if self.default_factory is ABSENT:
            if (issubclass(typ, (Data, _Text, Coords))
                    or not issubclass(typ, _Container)):
                self.default_factory = type(None)
            else:
                self.default_factory = typ if is_concrete else concrete

        if self.precheck is ABSENT and self.convert is ABSENT:
            self.precheck = precheck

        if self.convert is ABSENT:
            if issubclass(typ, Data):
                self.convert = typ.from_dict
            elif issubclass(typ, L):
                self.convert = lambda t: typ(*t)
            else:
                self.convert = typ if is_concrete else concrete

        if self.revert is ABSENT:
            self.revert = revert


def _r_l(l: L, _) -> _Tuple[str, str]:
    return str(l), l.localised


def _r_text(t: _Text, _) -> str:
    return str(t)


def _r_bool(b: bool, _) -> bool:
    return bool(b)


def _r_int(i: _Integral, _) -> int:
    return int(i)


def _r_real(r: _Real, _) -> float:
    return float(r)


def _r_map(m: _Mapping, memo) -> dict:

    d = {}
    memo[id(m)] = d
    d.update((str(k), _deepcopy(m[k], memo)) for k, v in m.items())
    return d


def _r_coll(c: _Collection, memo) -> list:

    l = []
    memo[id(c)] = l
    l.extend(_deepcopy(i, memo) for i in c)
    return l


# noinspection PyArgumentList
_FUNC_DEFAULT_MATRIX = (
    # abstract,        concrete,  precheck,                           revert
    # ---------------- ---------- ----------------------------------- ---------
    (Data,             ABSENT,    lambda m: isinstance(m, _Mapping),  _deepcopy),  # noqa: E272
    (L,                ABSENT,    lambda t: isinstance(t[0], _Text),  _r_l),       # noqa: E272
    (_Text,            str,       lambda t: isinstance(t, _Text),     _r_text),    # noqa: E272
    (bool,             bool,      lambda b: b in (False, True),       _r_bool),    # noqa: E272
    (_Integral,        int,       lambda i: isinstance(i, _Integral), _r_int),     # noqa: E272
    (_Real,            float,     lambda r: isinstance(r, _Real),     _r_real),    # noqa: E272
    (_Mapping,         dict,      lambda m: isinstance(m, _Mapping),  _r_map),     # noqa: E272
    (_MutableSet,      set,       lambda i: isinstance(i, _Iterable), _r_coll),    # noqa: E272
    (_AbstractSet,     frozenset, lambda i: isinstance(i, _Iterable), _r_coll),    # noqa: E272
    (_MutableSequence, list,      lambda i: isinstance(i, _Iterable), _r_coll),    # noqa: E272
    (_Collection,      tuple,     lambda i: isinstance(i, _Iterable), _r_coll),    # noqa: E272
    (object,           ABSENT,    ABSENT,                             ABSENT),     # noqa: E272
)


def _py2key(name: str) -> str:

    return ''.join(
        (
            word.upper() if word.lower() in ('cqc', 'fid', 'id', 'ls', 'uss')
            else word if word[0].istitle()
            else word[0].title() + word[1:]
        )
        for word in name.split('_') if word
    )


def _key2py(key: str) -> str:

    words = []
    word = key[-1]

    for c in key[-2::-1]:

        candidate = c + word

        if candidate.islower() or candidate.isupper() or candidate.istitle():
            word = candidate

        else:
            words += [word.lower()]
            word = c

    words += [word.lower()]

    return '_'.join(reversed(words))
