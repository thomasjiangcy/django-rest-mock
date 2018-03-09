"""
Utility functions
"""

import ast
from decimal import Decimal

def validate_fake_val(fake_val, fake_func, minimum, maximum):
    if minimum:
        minimum = ast.literal_eval(minimum)
    if maximum:
        maximum = ast.literal_eval(maximum)

    if (isinstance(fake_val, int) or isinstance(fake_val, float) or isinstance(fake_val, Decimal)) and\
        (minimum or maximum):
        if minimum and not maximum:
            while fake_val < minimum:
                fake_val = fake_func()  # keep trying until fake_val > minimum
        elif minimum and maximum:
            while fake_val < minimum or fake_val > maximum:
                fake_val = fake_func()  # keep trying until minimum <= fake_val <= maximum
        elif not minimum and maximum:
            while fake_val > maximum:
                fake_val = fake_func()  # keep trying until fake_val <= maximum

    elif isinstance(fake_val, str) and (minimum or maximum):
        if minimum and not maximum:
            fake_val = fake_val[minimum:]
        elif minimum and maximum:
            fake_val = fake_val[minimum:maximum]
        elif not minimum and maximum:
            fake_val = fake_val[:maximum]

    # For all other data types, min/max attributes will have no effect
    return str(fake_val)  # make sure to return a 'str' type
