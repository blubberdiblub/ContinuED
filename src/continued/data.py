#!/usr/bin/env python3

from numbers import (
    Real as _Real,
)

from .types import (
    Attr as _Attr,
    Data as _Data,
)

from .types import Coords, L


class Body(_Data):

    name: str = _Attr(key='Body')
    id: int = _Attr(key='BodyID')
    type: str = _Attr(key='BodyType')


class Cargo(_Data):

    name: L = _Attr()
    count: int = _Attr()
    stolen: int = _Attr()


class Commodity(_Data):

    id: int = _Attr(key='id')
    name: L = _Attr()
    category: L = _Attr()
    buy_price: int = _Attr()
    sell_price: int = _Attr()
    mean_price: int = _Attr()
    stock_bracket: int = _Attr()
    demand_bracket: int = _Attr()
    stock: int = _Attr()
    demand: int = _Attr()
    consumer: bool = _Attr()
    producer: bool = _Attr()
    rare: bool = _Attr()


class Component(_Data):

    name: str = _Attr()
    percent: float = _Attr()


class ConflictFaction(_Data):

    name: str = _Attr()
    stake: str = _Attr()
    won_days: int = _Attr()


class Conflict(_Data):

    war_type: str = _Attr()
    status: str = _Attr()
    faction1: ConflictFaction = _Attr()
    faction2: ConflictFaction = _Attr()


class Economy(_Data):

    name: L = _Attr()
    proportion: float = _Attr()


class Effect(_Data):

    effect: L = _Attr()
    trend: str = _Attr()


class Engineer(_Data):

    engineer: str = _Attr()
    engineer_id: int = _Attr()


class EngineeredModifier(_Data):

    label: str = _Attr()
    value: float = _Attr()
    original_value: float = _Attr()
    less_is_good: bool = _Attr(revert=lambda b, _: int(b))


class Engineering(_Data):

    engineer: Engineer = _Attr(key=())
    blueprint_id: int = _Attr()
    blueprint_name: str = _Attr()
    level: int = _Attr()
    quality: float = _Attr()
    modifiers: tuple[EngineeredModifier, ...] = _Attr(
        convert=lambda seq: tuple(EngineeredModifier.from_dict(d) for d in seq),
    )


class EngineerProgress(Engineer):

    progress: str = _Attr()
    rank_progress: int = _Attr()
    rank: int = _Attr()


class ExplorationData(_Data):

    system_name: str = _Attr()
    num_bodies: int = _Attr()


class Faction(_Data):

    name: str = _Attr()
    faction_state: str = _Attr()


class Influence(_Data):

    system_address: int = _Attr()
    trend: str = _Attr()
    influence: str = _Attr()


class FactionEffect(_Data):

    faction: str = _Attr()
    effects: tuple[Effect, ...] = _Attr(
        convert=lambda seq: tuple(Effect.from_dict(d) for d in seq),
    )
    influence: tuple[Influence, ...] = _Attr(
        convert=lambda seq: tuple(Influence.from_dict(d) for d in seq),
    )
    reputation_trend: str = _Attr()
    reputation: str = _Attr()


class FactionState(_Data):

    state: str = _Attr()
    trend: int = _Attr()


class FactionFull(Faction):

    government: str = _Attr()
    influence: float = _Attr()
    allegiance: str = _Attr()
    happiness: L = _Attr()
    my_reputation: float = _Attr()
    active_states: tuple[FactionState, ...] = _Attr(
        convert=lambda seq: tuple(FactionState.from_dict(d) for d in seq),
    )
    recovering_states: tuple[FactionState, ...] = _Attr(
        convert=lambda seq: tuple(FactionState.from_dict(d) for d in seq),
    )
    pending_states: tuple[FactionState, ...] = _Attr(
        convert=lambda seq: tuple(FactionState.from_dict(d) for d in seq),
    )


class Market(_Data):

    market_id: int = _Attr()


class Material(_Data):

    name: L = _Attr()
    category: L = _Attr()
    count: int = _Attr()


class Materials(_Data):

    raw: tuple[Material, ...] = _Attr(
        convert=lambda seq: tuple(Material.from_dict(d) for d in seq),
    )
    manufactured: tuple[Material, ...] = _Attr(
        convert=lambda seq: tuple(Material.from_dict(d) for d in seq),
    )
    encoded: tuple[Material, ...] = _Attr(
        convert=lambda seq: tuple(Material.from_dict(d) for d in seq),
    )


class Mission(_Data):

    id: int = _Attr(key='MissionID')
    name: str = _Attr()
    # TODO: there is a LocalisedName instead of Name_Localised
    passenger_mission: bool = _Attr()
    expires: int = _Attr()


class Missions(_Data):

    active: tuple[Mission, ...] = _Attr(
        convert=lambda seq: tuple(Mission.from_dict(d) for d in seq),
    )
    failed: tuple[Mission, ...] = _Attr(
        convert=lambda seq: tuple(Mission.from_dict(d) for d in seq),
    )
    complete: tuple[Mission, ...] = _Attr(
        convert=lambda seq: tuple(Mission.from_dict(d) for d in seq),
    )


class Module(_Data):

    slot: str = _Attr()
    item: str = _Attr()
    on: bool = _Attr()
    power: float = _Attr()
    priority: int = _Attr()
    health: float = _Attr()
    ammo_in_clip: int = _Attr()
    ammo_in_hopper: int = _Attr()
    engineering: Engineering = _Attr()


class ModulePrice(_Data):

    id: int = _Attr(key='id')
    name: str = _Attr()
    buy_price: int = _Attr()


class Ranking(_Data):

    combat: int = _Attr()
    trade: int = _Attr()
    explore: int = _Attr()
    empire: int = _Attr()
    federation: int = _Attr()
    cqc: int = _Attr()


# TODO: maybe merge Redeem and Reward
class Redeem(_Data):

    faction: str = _Attr()
    amount: int = _Attr()


# TODO: maybe merge Redeem and Reward
class Reward(_Data):

    faction: str = _Attr()
    reward: int = _Attr()


class Ring(_Data):

    name: str = _Attr()
    ring_class: str = _Attr()
    mass_mt: float = _Attr(key='MassMT')
    inner_rad: float = _Attr()
    outer_rad: float = _Attr()


class Ship(_Data):

    ship: L = _Attr()
    ship_id: int = _Attr()
    ship_name: str = _Attr()
    ship_ident: str = _Attr()
    unladen_mass: float = _Attr()
    hull_value: int = _Attr()
    modules_value: int = _Attr()
    hull_health: float = _Attr()
    cargo_capacity: int = _Attr()
    max_jump_range: float = _Attr()
    rebuy: int = _Attr()
    modules: tuple[Module, ...] = _Attr(
        convert=lambda seq: tuple(Module.from_dict(d) for d in seq),
    )


class ShipPrice(_Data):

    id: int = _Attr(key='id')
    ship_type: L = _Attr()
    ship_price: int = _Attr()


class Station(_Data):

    name: str = _Attr(key='StationName')
    type: str = _Attr(key='StationType')
    carrier_docking_access: str = _Attr()


class StationFull(Station):

    faction: Faction = _Attr(key='StationFaction')
    government: L = _Attr(key='StationGovernment')
    allegiance: str = _Attr(key='StationAllegiance')
    services: frozenset = _Attr(key='StationServices')
    economy: L = _Attr(key='StationEconomy')
    economies: tuple[Economy, ...] = _Attr(
        key='StationEconomies',
        convert=lambda seq: tuple(Economy.from_dict(d) for d in seq),
    )


class Statistics(_Data):

    bank_account: dict[str, int] = _Attr(key='Bank_Account')
    combat: dict[str, int] = _Attr()
    crime: dict[str, int] = _Attr()
    smuggling: dict[str, int] = _Attr()
    trading: dict[str, int] = _Attr()
    mining: dict[str, int] = _Attr()
    exploration: dict[str, int] = _Attr()
    passengers: dict[str, int] = _Attr()
    search_and_rescue: dict[str, int] = _Attr(key='Search_And_Rescue')
    crafting: dict[str, int] = _Attr()
    crew: dict[str, int] = _Attr()
    multicrew: dict[str, int] = _Attr()
    material_trader: dict[str, int] = _Attr(key='Material_Trader_Stats')
    cqc: dict[str, int] = _Attr()


class StoredModule(_Data):

    name: L = _Attr()
    storage_slot: int = _Attr()
    star_system: str = _Attr()
    market_id: int = _Attr()
    transfer_cost: int = _Attr()
    transfer_time: int = _Attr()
    in_transit: bool = _Attr()
    buy_price: int = _Attr()
    hot: bool = _Attr()


class StoredShip(_Data):

    ship_id: int = _Attr()
    ship_type: L = _Attr()
    name: str = _Attr()
    star_system: str = _Attr()
    ship_market_id: int = _Attr()
    transfer_price: int = _Attr()
    transfer_time: int = _Attr()
    in_transit: bool = _Attr()
    value: int = _Attr()
    hot: bool = _Attr()


class System(_Data):

    star_system: str = _Attr()
    system_address: int = _Attr()
    star_pos: Coords = _Attr(
        precheck=lambda seq: len(seq) == 3,
        convert=lambda seq: Coords(*(float(v) for v in seq)),
        validate=lambda seq: all(isinstance(v, _Real) for v in seq),
        revert=lambda seq, _: list(seq),
    )
    star_class: str = _Attr()


class SystemFull(System):

    allegiance: str = _Attr(key='SystemAllegiance')
    economy: L = _Attr(key='SystemEconomy')
    second_economy: L = _Attr(key='SystemSecondEconomy')
    government: L = _Attr(key='SystemGovernment')
    security: L = _Attr(key='SystemSecurity')
    population: int = _Attr()
