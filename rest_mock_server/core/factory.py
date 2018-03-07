"""
Factory class to generate fake values
"""

import ast
import json
import operator
import random
import re
from copy import deepcopy
from decimal import Decimal
from functools import reduce

from faker import Faker

fake = Faker()

class FixtureFactory:

    PYTHON_DATATYPES = ['str', 'int', 'float', 'decimal', 'set', 'dict', 'list', 'tuple', 'bool']
    META_KEYS = ['__mockcount', '__key_position', '__relationships']
    RELATIONSHIPS = [
        "count",
    ]

    def __init__(self, fake_response, parser_instance):
        self.parser_instance = parser_instance  # mainly to access fixtures if any
        self._is_empty = False  # remote controller for unique values - re.sub should return empty value

        self.fake_response = fake_response
        self.relationships = []
        self.relationship_targets = []
        self.total_count = 1

        # First, check for any relationships declared
        if '__relationships' in self.fake_response.keys():
            relationships = fake_response['__relationships']
            if relationships:
                for r in relationships:
                    # Parse the relationship string
                    parsed = r.split("__")
                    if not parsed:
                        raise ValueError(
                            'Please ensure that relationships are defined in the right syntax'
                            '<source-relationship>__<relationship>__<target-relationship>'
                        )
                    source, relationship, target = parsed
                    if relationship not in self.RELATIONSHIPS:
                        raise ValueError('Invalid relationship: %s' % relationship)
                    rs = {
                        'source': source,
                        'relationship': relationship,
                        'target': target
                    }
                    self.relationships.append(rs)
                    self.relationship_targets.append(target)

        # Second, check for any indication of duplication
        if '__mockcount' in fake_response.keys():
            self.total_count = fake_response['__mockcount']

    @staticmethod
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

    def handle_other_factory_method(self, attr, minimum, maximum):
        if attr == 'percentage':
            if minimum:
                minimum = ast.literal_eval(minimum)
            else:
                minimum = 0
            if maximum:
                maximum = ast.literal_eval(maximum)
            else:
                maximum = 100
            val = random.uniform(minimum, maximum)
            return val

    def replace_faker_attr(self, matchobj):
        attr = matchobj.group(0).replace('<', '').replace('>', '')
        # Prepare template to handle quotes
        template = '{}{}{}'
        startswithquote = ''
        endswithquote = ''
        if attr.startswith('"') or attr.startswith("'"):
            startswithquote = '"'
        if attr.endswith('"') or attr.endswith("'"):
            endswithquote = '"'

        # Check if uniqueness is required
        # We will need to maintain a temporary state to keep track of values
        is_unique = False
        if attr.startswith("'^") or attr.startswith("^"):
            is_unique = True
            attr = attr[2:] if attr.startswith("'^") else attr[1:]
            temp_state = getattr(self, attr.strip("'") + '__temp_state', None)
            if temp_state is None:
                setattr(self, attr.strip("'") + '__temp_state', [])
                temp_state = []

        if 'fk__' in attr:
            attr_map = [x.replace('"', '').replace("'", '') for x in attr.replace('fk__', '').split('.')]
            source_value = reduce(operator.getitem, attr_map, self._response_holder)
            if isinstance(source_value, str):
                return template.format(startswithquote, source_value, endswithquote)
            return source_value

        if '__from__' in attr:
            target, source = [x.replace('"', '').replace("'", '') for x in attr.split('__from__')]
            if self.parser_instance.fixture_data is not None:
                target_val_store = getattr(self, target + '_store', None)

                if target_val_store is None:
                    try:
                        source_data = self.parser_instance.fixture_data[source]
                        target_val_store = []
                        if isinstance(source_data, list):
                            for data in source_data:
                                if target == 'pk':
                                    target_val_store.append(data['pk'])
                                else:
                                    for k, v in data['fields'].items():
                                        if k == target:
                                            target_val_store.append(v)
                        setattr(self, target + '_store', target_val_store)
                    except KeyError:
                        raise ValueError('Fixture %s not found' % source)

                if target_val_store:
                    val = random.choice(target_val_store)
                    if is_unique:
                        while True:
                            if val not in temp_state:
                                temp_state.append(val)
                                setattr(self, attr.strip("'") + '__temp_state', temp_state)
                                break
                            if all(x in temp_state for x in target_val_store):
                                self._is_empty = True
                                break
                            val = random.choice(target_val_store)
                    if not isinstance(val, str):
                        return json.dumps(val)
                    return template.format(startswithquote, val, endswithquote)
                else:
                    return
            else:
                raise ValueError('No fixtures found')

        # Check if optional arguments are specified - syntax is <attr:min:max>
        _split = [x.replace("'", '').replace('"', '') for x in attr.split(":")]
        if len(_split) > 1:
            # Get the attr and value range (min/max)
            attr, val_range = _split[0], _split[1:]
            if len(val_range) > 1:
                minimum, maximum = val_range
            else:
                minimum, maximum = val_range[0], 0
        else:
            attr, minimum, maximum = _split[0], 0, 0
        # Min, max will be applied in a slice function if the data is a string
        attr_copy = attr  # keep a copy of original attribute
        if attr in self.PYTHON_DATATYPES:
            attr = 'py' + attr
        try:
            fake_func = getattr(fake, attr)
            fake_val = fake_func()
            fake_val = self.validate_fake_val(fake_val, fake_func, minimum, maximum)
        except AttributeError:
            # Check other methods
            fake_val = self.handle_other_factory_method(attr, minimum, maximum)

        if is_unique:
            while True:
                if fake_val not in temp_state:
                    break
                fake_val = fake_func()
                fake_val = self.validate_fake_val(fake_val, fake_func, minimum, maximum)
            temp_state.append(fake_val)
            setattr(self, attr.strip("'") + '__temp_state', temp_state)

        if attr_copy in ['int', 'float']:
            return fake_val
        return template.format(startswithquote, fake_val, endswithquote)

    def _parse_syntax(self, raw):
        raw = str(raw)  # treat the value as a string regardless of its actual data type
        has_syntax = re.findall(r'<(\^)?(fk__)?(\w+)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?>', raw, flags=re.DOTALL)

        if has_syntax:
            fake_val = re.sub(
                r'\'?\"?<(\^)?(fk__)?(\w+)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?>\'?\"?',
                self.replace_faker_attr,
                raw,
                flags=re.DOTALL
            )
            fake_val = fake_val.replace("'", '"')
            try:
                fake_val = json.loads(fake_val)
            except:
                pass
            return fake_val
        else:
            return raw

    def count(self, source, target):
        """
        The 'count' relationship is used for listing endpoints where a specific attribute
        might hold the value to the number of instances of another attribute.
        """
        try:
            source_value = self._response_holder[source]
        except KeyError:
            # source value hasn't been determined yet, we need
            # to generate the source value first
            raw = self.fake_response[source]
            source_value = self._parse_syntax(raw)
        if isinstance(source_value, str):
            source_value = int(source_value)
        target = self.fake_response[target]
        values = []
        for _ in range(source_value):
            self._is_empty = False  # remote state for re.sub to switch in case it hits a None value
            def get_mock_value(target):
                mock_value = self._parse_syntax(target)
                mock_value = str(mock_value)  # treat the value as a string regardless of its actual data type
                _target = str(mock_value)
                _target = _target[1:-1]
                _target = _target.replace("'", '"')

                try:
                    mock_value = json.loads(_target)
                except:
                    mock_value = _target
                return mock_value
            mock_value = get_mock_value(target)
            if not self._is_empty:
                values.append(mock_value)
        return values

    def _relationship_handler(self, source, relationship, target):
        handler = getattr(self, relationship)
        return handler(source, target)

    def generate(self):
        generated_responses = []
        for _ in range(self.total_count):
            self._is_empty = False
            self._response_holder = {}
            key_type, key_name, key_position = [None] * 3
            for k, v in self.fake_response.items():
                self._is_empty = False
                # Skip meta keys
                if k in self.META_KEYS:
                    continue

                # Check if key is in relationship
                for r in self.relationships:
                    self._is_empty = False
                    if r['target'] == k:
                        # If current key is defined as a relationship target
                        # then we need to handle it first
                        value = self._relationship_handler(
                            r['source'],
                            r['relationship'],
                            r['target']
                        )
                        self._response_holder[k] = value
                        continue

                if k == '__key':
                    try:
                        key_position = self.fake_response['__key_position']
                    except KeyError:
                        raise Exception("'__key_position' must be present if '__key' is present")
                    v = v.replace('<', '').replace('>', '')
                    key_name, key_type = v.split(':')
                elif k not in self.relationship_targets:
                    # Check if value fulfils the dynamic syntax
                    val = self._parse_syntax(v)
                    if k == 'confidentiality':
                        print(val)
                    if self._is_empty:
                        continue
                    self._response_holder[k] = val

            self._response_holder['__key_type'] = key_type
            self._response_holder['__key_position'] = key_position
            self._response_holder['__key_name'] = key_name
            generated_responses.append(str(self._response_holder))
        return generated_responses
