from aiogram import Router

import routers
from utils.find_attributes_recursively import find_attributes_recursively


def get_routers() -> list:
    """Retrieves all application routers from nested modules within the `src` module.

    This function searches for all instances of `APIRouter` defined in any module named "routes"
    within the `src` package and its subpackages.

    :return: A list of `APIRouter` instances found in the "routes" modules across the application.
    :rtype: list
    """
    return list(
        find_attributes_recursively(
            module=routers,
            attribute_type=Router,
            match_module_name="routes",
        ).values(),
    )
