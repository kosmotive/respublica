import random

from world.models import (
    World,
    Movable,
    Sector,
    Celestial,
    Unveiled,
)
from .indexing import *

import numpy as np
import yaml


def craete_random_sector_name():
    part1 = random.choice(greek_titans)
    part2 = random.choice(greek_letters)
    return f'{part1.capitalize()} {part2.capitalize()}'


def create_sector(used_names, x, y):
    name = None
    while name is None or name in used_names:
        name = craete_random_sector_name()

    sector = Sector.objects.create(
        position_x = x,
        position_y = y,
        name = name)

    with open('celestials.yml') as fp:
        recipes = yaml.safe_load(fp)

    num_celestials = random.randint(1, 10)
    for position in range(num_celestials):

        compatible_recipes = list()
        for recipe in recipes:
            if recipe.get('min-position', 0) <= position <= recipe.get('max-position', np.inf):
                compatible_recipes.append(recipe)

        recipe = random.choice(compatible_recipes)
        features = dict()
        for feature in recipe.keys():
            if feature.startswith('min-'):
                basename = feature[4:]
                if basename == 'position': continue
                minval = recipe[feature]
                maxval = recipe['max-' + basename]
                assert type(minval) is type(maxval)
                features[basename] = random.randint(minval, maxval) if type(minval) is int else random.uniform(minval, maxval)
            elif feature.startswith('max-'):
                pass
            else:
                features[feature] = recipe[feature]

        Celestial.objects.create(
            sector   = sector,
            position = position,
            features = features)

    return sector


def generate_world(radius, density, seed, exist_ok=False, tickrate=60):
    assert isinstance(radius, int) and radius > 0, radius
    assert 0 < density < 1, density
    assert exist_ok or Sector.objects.count() == 0

    from django.core.management import call_command
    call_command('flush', interactive=False)

    random.seed(seed)

    world = World.objects.create(id = 1, tickrate = tickrate)

    used_names = set()
    world_size = 2 * radius + 1
    for x, y in np.ndindex(world_size, world_size):
        if x ** 2 + y ** 2 > radius ** 2: continue
        if random.random() <= density:

            sector = create_sector(used_names, x, y)
            used_names.add(sector.name)

    return world


def generate_test_world(*args, **kwargs):
    world = generate_world(*args, **kwargs)

    # Create empire
    from game.models import Empire, Blueprint, Ship
    empire = Empire.objects.create(name = 'Foos')

    # Find a habitable planet
    celestial = Celestial.objects.filter(features__capacity__gte = 1)[0]
    celestial.habitated_by = empire
    celestial.save()

    # Add a movable ship
    ship = Ship.objects.create(
        blueprint = Blueprint.objects.get(
            empire = empire,
            base_id = 'ships/colony-ship'),
        movable = Movable.objects.create(
            position_x = celestial.sector.position_x,
            position_y = celestial.sector.position_y))

    # Unveil the neighborhood
    Unveiled.unveil(empire, celestial.sector.position, 1)
