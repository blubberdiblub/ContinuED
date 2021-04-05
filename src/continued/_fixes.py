#!/usr/bin/env python3

from .types import (
    Attr as _Attr,
)

from . import data as _data


class BodyForScanEvent(_data.Body):

    name: str = _Attr(key='BodyName')


BodyForScanEvent.__name__ = BodyForScanEvent.__base__.__name__


class ShipForTransfer(_data.StoredShip):

    star_system: str = _Attr(key='System')


ShipForTransfer.__name__ = ShipForTransfer.__base__.__name__
