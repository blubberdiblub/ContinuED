#!/usr/bin/env python3

from functools import total_ordering as _total_ordering

from numbers import (
    Integral as _Integral,
    Real as _Real,
)

from .types import (
    Attr as _Attr,
    Coords as _Coords,
    Data as _Data,
    DateTime as _DateTime,
    L,
)

from . import data
from . import _fixes


@_total_ordering
class Event(_Data):

    _event_name: str = _Attr(key='event', param='event')
    _timestamp: _DateTime = _Attr(
        key='timestamp',
        param=None,
        default_factory=_DateTime.now,
        convert=_DateTime.from_elite_string,
        revert=lambda dt, _: dt.to_elite_string(),
    )

    @classmethod
    def __init_subclass__(cls: 'Event', **kwargs) -> None:

        event_name = kwargs.pop('event_name', cls.__name__)
        if event_name:
            # noinspection PyTypeChecker
            cls._event_name = _Attr(
                name='_event_name', type_=str, key='event', param=None,
                default=event_name, precheck=lambda x: x == event_name,
            )

        super().__init_subclass__(**kwargs)

    def __eq__(self, other) -> bool:

        if not isinstance(other, type(self)):
            return NotImplemented

        return ((self._event_name, self._timestamp) ==
                (other._event_name, other._timestamp))

    def __lt__(self, other) -> bool:

        if not isinstance(other, type(self)):
            return NotImplemented

        if self._event_name != other._event_name:
            raise ValueError("cannot order events of different type")

        return self._timestamp < other._timestamp


class LogEvent(Event, event_name=None):

    _all: dict[str, 'LogEvent'] = {}

    @classmethod
    def __init_subclass__(cls: 'LogEvent', **kwargs) -> None:

        event_name = kwargs.get('event_name', cls.__name__)
        if event_name:
            cls._all[event_name] = cls

        super().__init_subclass__(**kwargs)


class UnknownEvent(LogEvent, event_name=None):

    pass


class ApproachBody(LogEvent):

    system: data.System = _Attr(key=())
    body: data.Body = _Attr(key=())


class ApproachSettlement(LogEvent, data.Market):

    name: str = _Attr()
    system_address: int = _Attr()
    body: _fixes.BodyForScanEvent = _Attr(key=())
    latitude: float = _Attr()
    longitude: float = _Attr()


class Bounty(LogEvent):

    rewards: tuple[data.Reward, ...] = _Attr(
        convert=lambda seq: tuple(data.Reward.from_dict(d) for d in seq)
    )
    target: L = _Attr()
    total_reward: int = _Attr()
    victim_faction: str = _Attr()


class BuyAmmo(LogEvent):

    cost: int = _Attr()


class BuyTradeData(LogEvent):

    system: str = _Attr()
    cost: int = _Attr()


class Cargo(LogEvent):

    vessel: str = _Attr()
    count: int = _Attr()
    inventory: tuple[data.Cargo, ...] = _Attr(
        convert=lambda seq: tuple(data.Cargo.from_dict(d) for d in seq),
    )


class CodexEntry(LogEvent):

    id: int = _Attr(key='EntryID')
    name: L = _Attr()
    category: L = _Attr()
    sub_category: L = _Attr()
    region: L = _Attr()
    system: str = _Attr()
    system_address: int = _Attr()
    nearest_destination: str = _Attr()
    is_new_entry: bool = _Attr()


class CollectCargo(LogEvent):

    type: L = _Attr()
    stolen: bool = _Attr()
    mission_id: int = _Attr()


class Commander(LogEvent):

    fid: str = _Attr(key='FID')
    name: str = _Attr()


class CommitCrime(LogEvent):

    crime_type: str = _Attr()
    faction: str = _Attr()
    fine: int = _Attr()
    bounty: int = _Attr()


class CrewAssign(LogEvent):

    name: str = _Attr()
    crew_id: int = _Attr()
    role: str = _Attr()


class Died(LogEvent):

    killer_name: str = _Attr()
    killer_ship: str = _Attr()
    killer_rank: str = _Attr()


class Docked(LogEvent, data.Market):

    station: data.StationFull = _Attr(key=())
    dist_from_star_ls: float = _Attr()
    system: data.System = _Attr(key=())


class DockingDenied(LogEvent, data.Market):

    reason: str = _Attr()
    station: data.Station = _Attr(key=())


class DockingGranted(LogEvent, data.Market):

    landing_pad: int = _Attr()
    station: data.Station = _Attr(key=())


class DockingRequested(LogEvent, data.Market):

    station: data.Station = _Attr(key=())


class EngineerProgress(LogEvent):

    engineers: tuple[data.EngineerProgress, ...] = _Attr(
        convert=lambda seq: tuple(data.EngineerProgress.from_dict(d)
                                  for d in seq)
    )


class EscapeInterdiction(LogEvent):

    interdictor: str = _Attr()
    is_player: bool = _Attr()


class FSDJump(LogEvent):

    system: data.SystemFull = _Attr(key=())
    body: data.Body = _Attr(key=())
    jump_dist: float = _Attr()
    fuel_used: float = _Attr()
    fuel_level: float = _Attr()
    factions: tuple[data.Faction, ...] = _Attr(
        convert=lambda seq: tuple(data.FactionFull.from_dict(d) for d in seq),
    )
    system_faction: data.Faction = _Attr()
    conflicts: tuple[data.Conflict, ...] = _Attr(
        convert=lambda seq: tuple(data.Conflict.from_dict(d) for d in seq),
    )


class FSDTarget(LogEvent):

    name: str = _Attr()
    system: data.System = _Attr(key=())
    remaining_jumps_in_route: int = _Attr()


class FSSAllBodiesFound(LogEvent):

    system_name: str = _Attr()
    system_address: int = _Attr()
    count: int = _Attr()


class FSSDiscoveryScan(LogEvent):

    progress: float = _Attr()
    body_count: int = _Attr()
    non_body_count: int = _Attr()
    system_name: str = _Attr()
    system_address: int = _Attr()


class FSSSignalDiscovered(LogEvent):

    system_address: int = _Attr()
    signal_name: L = _Attr()
    is_station: bool = _Attr()
    uss_type: L = _Attr()
    spawning_state: L = _Attr()
    spawning_faction: L = _Attr()
    threat_level: int = _Attr()


class FuelScoop(LogEvent):

    scooped: float = _Attr()
    total: float = _Attr()


class HullDamage(LogEvent):

    health: float = _Attr()
    player_pilot: bool = _Attr()
    fighter: bool = _Attr()


class Interdicted(LogEvent):

    submitted: bool = _Attr()
    interdictor: str = _Attr()
    is_player: bool = _Attr()
    faction: str = _Attr()


class LeaveBody(LogEvent):

    system: data.System = _Attr(key=())
    body: data.Body = _Attr(key=())


class LoadGame(LogEvent):

    fid: str = _Attr(key='FID')
    commander: str = _Attr()
    horizons: bool = _Attr()
    ship: data.Ship = _Attr(key=())
    fuel_level: float = _Attr()
    fuel_capacity: float = _Attr()
    game_mode: str = _Attr()
    credits: int = _Attr()
    loan: int = _Attr()


class Loadout(LogEvent):

    ship: data.Ship = _Attr(key=())
    fuel_capacity: dict[str, float] = _Attr()
    # modules: tuple = _Attr()


class Location(LogEvent, data.Market):

    station: data.StationFull = _Attr(key=())
    docked: bool = _Attr()
    system: data.SystemFull = _Attr(key=())
    body: data.Body = _Attr(key=())
    factions: tuple[data.Faction, ...] = _Attr(
        convert=lambda seq: tuple(data.FactionFull.from_dict(d) for d in seq),
    )
    system_faction: data.Faction = _Attr()
    conflicts: tuple[data.Conflict, ...] = _Attr(
        convert=lambda seq: tuple(data.Conflict.from_dict(d) for d in seq),
    )


class Market(LogEvent, data.Market):

    star_system: str = _Attr()
    station: data.Station = _Attr(key=())
    commodities: tuple[data.Commodity, ...] = _Attr(
        key='Items',
        convert=lambda seq: tuple(data.Commodity.from_dict(d) for d in seq),
    )


class MarketBuy(LogEvent, data.Market):

    type: L = _Attr()
    count: int = _Attr()
    buy_price: int = _Attr()
    total_cost: int = _Attr()


class MarketSell(LogEvent, data.Market):

    type: L = _Attr()
    count: int = _Attr()
    sell_price: int = _Attr()
    total_sale: int = _Attr()
    avg_price_paid: int = _Attr()


class MaterialCollected(LogEvent):

    category: str = _Attr()
    material: data.Material = _Attr(key=())


class Materials(LogEvent):

    materials: data.Materials = _Attr(key=())


class MissionAbandoned(LogEvent):

    mission: data.Mission = _Attr(key=())


class MissionAccepted(LogEvent):

    mission: data.Mission = _Attr(key=())
    faction: str = _Attr()
    target: L = _Attr()
    target_faction: str = _Attr()
    commodity: L = _Attr()
    count: int = _Attr()
    destination_system: str = _Attr()
    destination_station: str = _Attr()
    expiry: _DateTime = _Attr(
        default_factory=type(None),
        convert=_DateTime.from_elite_string,
        revert=lambda dt, _: dt.to_elite_string(),
    )
    wing: bool = _Attr()
    influence: str = _Attr()
    reputation: str = _Attr()
    reward: int = _Attr()


class MissionCompleted(LogEvent):

    mission: data.Mission = _Attr(key=())
    faction: str = _Attr()
    target_faction: str = _Attr()
    destination_system: str = _Attr()
    destination_station: str = _Attr()
    reward: int = _Attr()
    commodity_reward: tuple[data.Cargo, ...] = _Attr(
        convert=lambda seq: tuple(data.Cargo.from_dict(d) for d in seq),
    )
    materials_reward: tuple[data.Material, ...] = _Attr(
        convert=lambda seq: tuple(data.Material.from_dict(d) for d in seq),
    )
    faction_effects: tuple[data.FactionEffect, ...] = _Attr(
        convert=lambda seq: tuple(data.FactionEffect.from_dict(d) for d in seq),
    )


class MissionRedirected(LogEvent):

    mission: data.Mission = _Attr(key=())
    new_destination_station: str = _Attr()
    new_destination_system: str = _Attr()
    old_destination_station: str = _Attr()
    old_destination_system: str = _Attr()


class Missions(LogEvent):

    missions: data.Missions = _Attr(key=())


class ModuleBuy(LogEvent, data.Market):

    slot: str = _Attr()
    buy_item: L = _Attr()
    buy_price: int = _Attr()
    sell_item: L = _Attr()
    sell_price: int = _Attr()
    ship: data.Ship = _Attr(key=())


class ModuleInfo(LogEvent):

    modules: tuple[data.Module, ...] = _Attr(
        convert=lambda seq: tuple(data.Module.from_dict(d) for d in seq),
    )


class MultiSellExplorationData(LogEvent):

    discovered: tuple[data.ExplorationData, ...] = _Attr(
        convert=lambda seq: tuple(data.ExplorationData.from_dict(d)
                                  for d in seq),
    )
    base_value: int = _Attr()
    bonus: int = _Attr()
    total_earnings: int = _Attr()


class Music(LogEvent):

    music_track: str = _Attr()


class NavRoute(LogEvent):

    route: tuple[data.System, ...] = _Attr(
        convert=lambda seq: tuple(data.System.from_dict(d) for d in seq),
    )


class NpcCrewPaidWage(LogEvent):

    npc_crew_id: int = _Attr(key='NpcCrewId')
    npc_crew_name: str = _Attr()
    amount: int = _Attr()


class Outfitting(LogEvent, data.Market):

    star_system: str = _Attr()
    station_name: str = _Attr()
    horizons: bool = _Attr()
    modules: tuple[data.ModulePrice, ...] = _Attr(
        key='Items',
        convert=lambda seq: tuple(data.ModulePrice.from_dict(d) for d in seq),
    )


class Progress(LogEvent):

    ranking: data.Ranking = _Attr(key=())


class Promotion(LogEvent):

    ranking: data.Ranking = _Attr(key=())


class Rank(LogEvent):

    ranking: data.Ranking = _Attr(key=())


class ReceiveText(LogEvent):

    from_: L = _Attr()
    channel: str = _Attr()
    message: L = _Attr()


class RedeemVoucher(LogEvent):

    type: str = _Attr()
    amount: int = _Attr()
    factions: tuple[data.Redeem, ...] = _Attr(
        convert=lambda seq: tuple(data.Redeem.from_dict(d) for d in seq),
    )


class RefuelAll(LogEvent):

    cost: int = _Attr()
    amount: float = _Attr()


class RefuelPartial(LogEvent):

    cost: int = _Attr()
    amount: float = _Attr()


class Repair(LogEvent):

    item: L = _Attr()
    multiple: tuple[str, ...] = _Attr(key='Items', convert=tuple)
    cost: int = _Attr()


class RepairAll(LogEvent):

    cost: int = _Attr()


class Reputation(LogEvent):

    empire: float = _Attr()
    federation: float = _Attr()
    independent: float = _Attr()
    alliance: float = _Attr()


class ReservoirReplenished(LogEvent):

    fuel_main: float = _Attr()
    fuel_reservoir: float = _Attr()


class Resurrect(LogEvent):

    option: str = _Attr()
    cost: int = _Attr()
    bankrupt: bool = _Attr()


class Scan(LogEvent):

    scan_type: str = _Attr()
    body: _fixes.BodyForScanEvent = _Attr(key=())
    parents: tuple[dict[str, int], ...] = _Attr()
    system: data.System = _Attr(key=())
    distance_from_arrival_ls: float = _Attr()
    star_type: str = _Attr()
    subclass: int = _Attr()
    tidal_lock: bool = _Attr()
    terraform_state: str = _Attr()
    planet_class: str = _Attr()
    atmosphere: str = _Attr()
    atmosphere_type: str = _Attr()
    atmosphere_composition: tuple[data.Component, ...] = _Attr(
        convert=lambda seq: tuple(data.Component.from_dict(d) for d in seq),
    )
    volcanism: str = _Attr()
    stellar_mass: float = _Attr()
    mass_em: float = _Attr(key='MassEM')
    radius: float = _Attr()
    absolute_magnitude: float = _Attr()
    age_my: int = _Attr(key='Age_MY')
    surface_gravity: float = _Attr()
    surface_temperature: float = _Attr()
    surface_pressure: float = _Attr()
    luminosity: str = _Attr()
    landable: bool = _Attr()
    materials: tuple[data.Component, ...] = _Attr(
        convert=lambda seq: tuple(data.Component.from_dict(d) for d in seq),
    )
    composition: dict[str, float] = _Attr()
    semi_major_axis: float = _Attr()
    eccentricity: float = _Attr()
    orbital_inclination: float = _Attr()
    periapsis: float = _Attr()
    orbital_period: float = _Attr()
    rotation_period: float = _Attr()
    axial_tilt: float = _Attr()
    rings: tuple[data.Ring, ...] = _Attr(
        convert=lambda seq: tuple(data.Ring.from_dict(d) for d in seq)
    )
    reserve_level: str = _Attr()
    was_discovered: bool = _Attr()
    was_mapped: bool = _Attr()


class Scanned(LogEvent):

    scan_type: str = _Attr()


class SellExplorationData(LogEvent):

    systems: tuple[str] = _Attr()
    discovered: tuple[data.ExplorationData, ...] = _Attr(
        convert=lambda seq: tuple(data.ExplorationData.from_dict(d)
                                  for d in seq),
    )
    base_value: int = _Attr()
    bonus: int = _Attr()
    total_earnings: int = _Attr()


class ShipTargeted(LogEvent):

    target_locked: bool = _Attr()
    ship: L = _Attr()
    scan_stage: int = _Attr()
    pilot_name: L = _Attr()
    pilot_rank: str = _Attr()
    shield_health: float = _Attr()
    hull_health: float = _Attr()
    faction: str = _Attr()
    legal_status: str = _Attr()
    bounty: int = _Attr()


class Shipyard(LogEvent, data.Market):

    station: data.Station = _Attr(key=())
    star_system: str = _Attr()
    horizons: bool = _Attr()
    allow_cobra_mk_iv: bool = _Attr(key='AllowCobraMkIV')
    price_list: tuple[data.ShipPrice, ...] = _Attr(
        convert=lambda seq: tuple(data.ShipPrice.from_dict(d) for d in seq),
    )


class ShipyardSwap(LogEvent, data.Market):

    ship: data.StoredShip = _Attr(key=())
    store_old_ship: str = _Attr()
    store_ship_id: int = _Attr()


class ShipyardTransfer(LogEvent, data.Market):

    ship: _fixes.ShipForTransfer = _Attr(key=())
    distance: float = _Attr()


class Shutdown(LogEvent):

    pass


class StartJump(LogEvent):

    jump_type: str = _Attr()
    system: data.System = _Attr(key=())


class Statistics(LogEvent):

    statistics: data.Statistics = _Attr(key=())


class Status(Event):

    flags: int = _Attr()
    pips: tuple[int, int, int] = _Attr(
        precheck=lambda seq: len(seq) == 3,
        validate=lambda seq: all(isinstance(i, _Integral) for i in seq),
    )
    fire_group: int = _Attr()
    gui_focus: int = _Attr()
    fuel: dict[str, float] = _Attr()
    cargo: float = _Attr()
    legal_state: str = _Attr()


class StoredModules(LogEvent, data.Market):

    station: data.Station = _Attr(key=())
    system: data.System = _Attr(key=())
    modules: tuple[data.StoredModule, ...] = _Attr(
        key='Items',
        convert=lambda seq: tuple(data.StoredModule.from_dict(d) for d in seq),
    )


class StoredShips(LogEvent, data.Market):

    station_name: str = _Attr()
    star_system: str = _Attr()

    ships_here: tuple[data.StoredShip, ...] = _Attr(
        convert=lambda seq: tuple(data.StoredShip.from_dict(d) for d in seq),
    )
    ships_remote: tuple[data.StoredShip, ...] = _Attr(
        convert=lambda seq: tuple(data.StoredShip.from_dict(d) for d in seq),
    )


class SupercruiseEntry(LogEvent):

    system: data.System = _Attr(key=())


class SupercruiseExit(LogEvent):

    system: data.System = _Attr(key=())
    body: data.Body = _Attr(key=())


class UnderAttack(LogEvent):

    target: str = _Attr()


class Undocked(LogEvent, data.Market):

    station: data.Station = _Attr(key=())


class USSDrop(LogEvent):

    type: L = _Attr(key='USSType')
    threat: int = _Attr(key='USSThreat')
