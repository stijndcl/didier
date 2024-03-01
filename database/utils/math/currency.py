import math

__all__ = [
    "capacity_upgrade_price",
    "interest_upgrade_price",
    "rob_upgrade_price",
    "interest_rate",
    "savings_cap",
    "jail_chance",
    "jail_time",
    "rob_amount",
    "rob_chance",
]


def interest_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your interest level"""
    base_cost = 600
    growth_rate = 1.8

    return math.floor(base_cost * (growth_rate ** (level - 1)))


def capacity_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your capacity level"""
    base_cost = 800
    growth_rate = 1.6

    return math.floor(base_cost * (growth_rate ** (level - 1)))


def rob_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your rob level"""
    base_cost = 950
    growth_rate = 1.9

    return math.floor(base_cost * (growth_rate ** (level - 1)))


def interest_rate(level: int) -> float:
    """Calculate the amount of interest you will receive"""
    base_rate = 1.025
    growth_rate = 0.03

    return base_rate + (growth_rate * (level - 1))


def savings_cap(level: int) -> int:
    """Calculate the maximum amount you can save"""
    base_limit = 1000
    growth_rate = 1.10

    return math.floor(base_limit * (growth_rate ** (level - 1)))


def jail_chance(level: int) -> float:
    """Calculate the chance that you'll end up in jail"""
    base_chance = 0.35
    growth_rate = 1.15

    return min(0.1, max(0.0, base_chance - (growth_rate**level)))


def jail_time(level: int) -> int:
    """Calculate the time in hours you'll have to spend in jail"""
    base_hours = 2
    growth_rate = 1.27

    return math.floor(base_hours + growth_rate**level)


def rob_amount(level: int) -> int:
    """Calculate the maximum amount of Didier Dinks that you can rob"""
    base_amount = 250
    growth_rate = 1.4

    return math.floor(base_amount * (growth_rate**level))


def rob_chance(level: int) -> float:
    """Calculate the chances of a robbing attempt being successful"""
    base_chance = 0.25

    return base_chance + 2.1 * level
