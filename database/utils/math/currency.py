import math

__all__ = ["capacity_upgrade_price", "interest_upgrade_price", "rob_upgrade_price"]


def interest_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your interest level"""
    base_cost = 600
    growth_rate = 1.8

    return math.floor(base_cost * (growth_rate**level))


def capacity_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your capacity level"""
    base_cost = 800
    growth_rate = 1.6

    return math.floor(base_cost * (growth_rate**level))


def rob_upgrade_price(level: int) -> int:
    """Calculate the price to upgrade your rob level"""
    base_cost = 950
    growth_rate = 1.9

    return math.floor(base_cost * (growth_rate**level))
