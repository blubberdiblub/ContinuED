#!/usr/bin/env python3

from typing import Any, Deque, Dict, Optional, Set, Type, Union

import dataclasses
import json
import os
import pathlib
import re

from collections import deque
from contextvars import ContextVar
from functools import total_ordering

import trio
import trio_asyncio
import watchgod

from . import (
    events as _events,
    data as _data,
    types as _types,
)

from .logging import Logger as _Logger


_log = _Logger(__name__)


EventMap = ContextVar('event_map')


class _JournalWatcher(watchgod.watcher.AllWatcher):

    def __init__(self, root_path: trio.Path) -> None:

        super().__init__(pathlib.Path(root_path))

    def _walk(self, path: str, changes: Set['watchgod.watcher.FileChange'],
              new_files: Dict[str, float]) -> None:

        for entry in os.scandir(path):
            if entry.is_dir():
                continue

            if entry.name.endswith('.json'):
                self._watch_file(entry.path, changes, new_files, entry.stat())
                continue

            if not entry.name.endswith('.log'):
                continue

            self._watch_file(entry.path, changes, new_files,
                             os.stat(entry.path))

    def should_watch_dir(self, entry: 'watchgod.watcher.DirEntry') -> bool:
        return False

    def should_watch_file(self, entry: 'watchgod.watcher.DirEntry') -> bool:
        return entry.name.rsplit('.', maxsplit=1)[-1] in ('json', 'log')


@total_ordering
class _LogFile:

    @dataclasses.dataclass(order=True, frozen=True)
    class NameData:
        year: int
        month: int
        day: int
        hour: int
        minute: int
        second: int
        part: int = 1
        tag: str = ''
        suffix: str = ''

        def replace(self, **kwargs) -> '_LogFile.NameData':
            return dataclasses.replace(self, **kwargs)

    path: trio.Path
    name_data: Optional[NameData]

    FMT_FILENAME = ('Journal{tag}.'
                    '{year:02}{month:02}{day:02}'
                    '{hour:02}{minute:02}{second:02}'
                    '.{part:02}.log{suffix}')

    RE_FILENAME = re.compile(r'''(?:^|[/\\])
        Journal
        (?P<tag>\w*)\.
        (?P<year>\d{2,})
        (?P<month>(?:0[1-9]|1[0-2]))
        (?P<day>(?:0[1-9]|[12][0-9]|3[01]))
        (?P<hour>(?:[01][0-9]|2[0-3]))
        (?P<minute>[0-5][0-9])
        (?P<second>[0-5][0-9])
        \.(?P<part>0*[1-9][0-9]*)
        \.log(?P<suffix>\W.*)?
    $''', re.VERBOSE | re.IGNORECASE)

    def __init__(self, path: trio.Path,
                 name: Union[str, NameData] = None) -> None:

        self.path = trio.Path(path)

        if isinstance(name, self.NameData):
            if name.year < 1900:
                name = name.replace(year=name.year + 2000)
            self.name_data = name

            if 2000 <= name.year <= 2099:
                name = name.replace(year=name.year % 100)
            self.path /= self.FMT_FILENAME.format(**dataclasses.asdict(name))

        else:
            if name:
                self.path /= name

            m = self.RE_FILENAME.fullmatch(self.path.name)
            if m:
                year = int(m['year'])
                self.name_data = self.NameData(
                    year=year + 2000 if year < 1900 else year,
                    month=int(m['month']),
                    day=int(m['day']),
                    hour=int(m['hour']),
                    minute=int(m['minute']),
                    second=int(m['second']),
                    part=int(m['part']),
                    tag=m['tag'] or '',
                    suffix=m['suffix'] or '',
                )

            else:
                self.name_data = None

    def __repr__(self) -> str:

        cls = type(self)
        return f"{cls.__name__}({self.path!r})"

    def __bool__(self) -> bool:

        return self.name_data is not None

    def __eq__(self, other) -> bool:

        if not isinstance(other, type(self)):
            return NotImplemented

        return self.path == other.path

    def __lt__(self, other) -> bool:

        if not isinstance(other, type(self)):
            return NotImplemented

        if self.path.parent != other.path.parent:
            raise ValueError("cannot order journal logs in different folders")

        if self.name_data is None or other.name_data is None:
            raise ValueError("cannot order journal logs with invalid name")

        if self.name_data.tag != other.name_data.tag:
            raise ValueError("cannot order journal logs with different tags")

        return self.name_data < other.name_data

    # noinspection PyUnresolvedReferences,PyProtectedMember
    async def open(self, **kwargs) -> trio._file_io.AsyncIOWrapper:

        return await self.path.open(**kwargs)

    async def stat(self):

        return await self.path.stat()


class _Journal:

    _decoder: json.JSONDecoder

    log_file: Optional[_LogFile]

    timestamp: Optional[_types.DateTime]
    part: Optional[int]
    language: Optional[str]
    game_version = Optional[str]
    build = Optional[str]

    def __init__(self) -> None:

        self._decoder = json.JSONDecoder(strict=True)

        self.log_file = None

        self.timestamp = None
        self.part = None
        self.language = None
        self.game_version = None
        self.build = None

    # noinspection PyUnresolvedReferences,PyProtectedMember
    async def _parse_header(self, f: trio._file_io.AsyncIOWrapper) -> None:

        header = await f.readline()
        if not header.endswith(b'\x0a'):
            raise ValueError("invalid header")

        header = self._decoder.decode(header.decode('utf-8'))

        if header.get('event') != 'Fileheader':
            raise ValueError("invalid header")

        timestamp = header.get('timestamp')
        if timestamp:
            dt = _types.DateTime.from_elite_string(timestamp)
        else:
            st = await self.log_file.stat()
            dt = _types.DateTime.fromtimestamp(min(st.st_ctime, st.st_mtime))

        self.timestamp = dt

        part = header.get('part')
        self.part = int(part) if part else None

        self.language = header.get('language')
        self.game_version = header.get('gameversion')
        self.build = header.get('build')

    async def find_initial_log(self, journal_path: trio.Path) -> None:

        candidates = await journal_path.glob('Journal.*.*.log')
        candidates = filter(None, (_LogFile(path) for path in candidates))

        self.log_file = max(candidates, default=None)

    async def async_loop(self,
                         file_modified: trio.MemoryReceiveChannel) -> None:

        async with file_modified:

            while True:

                while not self.log_file:

                    path = await file_modified.receive()
                    self.log_file = _LogFile(path)

                async with await self.log_file.open(mode='rb') as f:

                    await self._handle_file(f, file_modified)

    # noinspection PyUnresolvedReferences,PyProtectedMember
    async def _handle_file(self, f: trio._file_io.AsyncIOWrapper,
                           file_modified: trio.MemoryReceiveChannel) -> None:

        event_map = EventMap.get()

        await self._parse_header(f)

        while True:
            async for line in f:
                assert line.endswith(b'\x0a')

                data = self._decoder.decode(line.decode('utf-8'))
                event_name = data.get('event')
                if event_name == 'Continued':
                    new_part = int(data['part'])
                    self.log_file = _LogFile(
                        self.log_file.path.parent,
                        name=self.log_file.name_data.replace(part=new_part)
                    )
                    return

                event = self._make_event(event_name, data)

                if data_file := event_map.get(event_name):
                    event = await self._enrich_event(data_file, event)

                if not self._handle_event(event):
                    self.log_file = None
                    return

            path = await file_modified.receive()
            while path == self.log_file.path:
                try:
                    path = await file_modified.receive_nowait()

                except trio.WouldBlock:
                    break
            else:
                self.log_file = _LogFile(path)
                return

    @staticmethod
    def _make_event(name: str, data: Dict[str, Any]) -> _events.LogEvent:

        try:
            # noinspection PyProtectedMember
            cls = _events.LogEvent._all[name]

        except KeyError:
            cls = _events.UnknownEvent

        return cls.from_dict(data, copy=False)

    # noinspection PyProtectedMember
    async def _enrich_event(self, data_file: '_DataFile',
                            event: _events.LogEvent) -> _events.LogEvent:

        with trio.move_on_after(10):
            candidate = await self._wait_data_file(data_file, event._timestamp)
            if candidate._timestamp == event._timestamp:
                return candidate

        return event

    @staticmethod
    async def _wait_data_file(
            data_file: '_DataFile', timestamp: _types.DateTime
    ) -> _events.LogEvent:

        async with data_file.updated:

            while True:
                event = data_file.find(timestamp)
                data_file.purge_up_to(timestamp)

                if event is not None:
                    return event

                await data_file.updated.wait()

    @staticmethod
    def _handle_event(event: _events.LogEvent) -> bool:

        if isinstance(event, _events.UnknownEvent):
            _log.debug(repr(event))
            return True

        _log.trace(repr(event))

        if isinstance(event, _events.Shutdown):
            return False

        return True


class _DataFile:

    event_name: str
    path: trio.Path
    updated: trio.Condition

    _event_cls: Type[_events.LogEvent]
    _buffer: Deque[_events.Event]
    _decoder: json.JSONDecoder

    def __init__(self, event_cls: Type[_events.LogEvent], path: trio.Path,
                 backlog: int = 10) -> None:

        self._event_cls = event_cls
        self.event_name = event_cls.__name__
        self.path = trio.Path(path)
        self.updated = trio.Condition()

        self._buffer = deque(maxlen=1 + backlog)
        self._decoder = json.JSONDecoder(strict=True)

    def __repr__(self) -> str:

        return f"{type(self).__name__}({self.path.parent!r})"

    def __eq__(self, other) -> bool:

        assert False, "supposedly unused"

        if not isinstance(other, type(self)):
            return NotImplemented

        return self.path == other.path

    def __hash__(self) -> int:

        assert False, "supposedly unused"

        return hash(self.path)

    def enqueue(self, event: _events.Event) -> None:

        if not self._buffer or event >= self._buffer[0]:
            self._buffer.appendleft(event)
            return

        # Supposedly very unlikely case (therefore not efficient):

        if len(self._buffer) == self._buffer.maxlen:
            self._buffer.pop()

        for i, compare in enumerate(self._buffer):
            if event >= compare:
                self._buffer.insert(i, event)
                break
        else:
            self._buffer.append(event)

    def find(self, timestamp: _types.DateTime) -> Optional[_events.Event]:

        if not self._buffer:
            return None

        event = self._buffer[0]
        if timestamp >= event._timestamp:
            return event if timestamp == event._timestamp else None

        # Supposedly very unlikely case (therefore not efficient):

        for event in reversed(self._buffer):
            if timestamp <= event._timestamp:
                return event

    def purge_up_to(self, timestamp: _types.DateTime) -> None:

        if not self._buffer:
            return

        if timestamp >= self._buffer[0]._timestamp:
            self._buffer.clear()
            return

        # Supposedly very unlikely case (therefore not efficient):

        while timestamp >= self._buffer[-1]._timestamp:
            self._buffer.pop()

    async def _read_data(self) -> Dict[str, Any]:

        data = await self.path.read_text(encoding='utf-8', errors='strict')
        data = self._decoder.decode(data)
        assert data.get('event') == self.event_name
        if 'timestamp' not in data:
            st = await self.path.stat()
            dt = _types.DateTime.fromtimestamp(st.st_mtime)
            data['timestamp'] = dt.to_elite_string()

        return data

    async def async_loop(self, file_modified: trio.MemoryReceiveChannel) -> None:

        async with file_modified:

            while True:

                try:
                    while True:
                        await file_modified.receive_nowait()

                except trio.WouldBlock:
                    pass

                try:
                    data = await self._read_data()
                    event = self._event_cls.from_dict(data, copy=False)

                except Exception as exc:
                    _log.exception(str(exc))

                else:
                    async with self.updated:
                        self.enqueue(event)
                        self.updated.notify_all()

                await file_modified.receive()


def spawn_json_tasks(
        nursery: trio.Nursery, journal_path: trio.Path
) -> dict[trio.Path, trio.MemorySendChannel]:

    watch_map = {}
    event_map = {}

    for event_cls, file_name in [
        (_events.Cargo, 'Cargo.json'),
        (_events.Market, 'Market.json'),
        (_events.ModuleInfo, 'ModulesInfo.json'),
        (_events.NavRoute, 'NavRoute.json'),
        (_events.Outfitting, 'Outfitting.json'),
        (_events.Shipyard, 'Shipyard.json'),
        (_events.Status, 'Status.json'),
    ]:
        data_file = _DataFile(event_cls, journal_path / file_name)

        send_endpoint, recv_endpoint = trio.open_memory_channel(0)
        nursery.start_soon(data_file.async_loop, recv_endpoint)

        watch_map[data_file.path] = send_endpoint
        event_map[data_file.event_name] = data_file

    EventMap.set(event_map)

    return watch_map


def spawn_log_task(
        nursery: trio.Nursery, journal: _Journal
) -> trio.MemorySendChannel:

    send_endpoint, recv_endpoint = trio.open_memory_channel(100)
    nursery.start_soon(journal.async_loop, recv_endpoint)

    return send_endpoint


async def watch_journal(
        awatch: watchgod.awatch,
        watch_map: dict[trio.Path, trio.MemorySendChannel],
        log_endpoint: trio.MemorySendChannel,
) -> None:

    async for changes in trio_asyncio.aio_as_trio(awatch):

        changed = {trio.Path(path) for change, path in changes
                   if change != watchgod.Change.deleted}

        if not changed:
            continue

        data_affected = changed.intersection(watch_map)
        log_affected = max(filter(
            (lambda log_file: log_file and not log_file.name_data.tag),
            (_LogFile(path) for path in changed - data_affected)
        ), default=None)

        for path in data_affected:
            watch_map[path].send_nowait(...)

        if data_affected and log_affected:
            await trio.sleep(0)

        if log_affected:
            log_endpoint.send_nowait(log_affected.path)


async def loop(task_status=trio.TASK_STATUS_IGNORED) -> None:

    journal_path = (await trio.Path.home()).joinpath(
        'Saved Games/Frontier Developments/Elite Dangerous'
    )

    journal = _Journal()
    await journal.find_initial_log(journal_path)

    awatch = watchgod.awatch(journal_path, watcher_cls=_JournalWatcher,
                             debounce=500, normal_sleep=200)
    awatch._executor = trio_asyncio.TrioExecutor(max_workers=2)

    async with trio.open_nursery() as nursery:

        watch_map = spawn_json_tasks(nursery, journal_path)
        log_endpoint = spawn_log_task(nursery, journal)

        task_status.started()

        await watch_journal(awatch, watch_map, log_endpoint)
