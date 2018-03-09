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

from .utils import validate_fake_val

fake = Faker()

class FixtureFactory:

    PYTHON_DATATYPES = ['str', 'int', 'float', 'decimal', 'set', 'dict', 'list', 'tuple', 'bool']
    META_KEYS = ['__mockcount', '__key_position', '__relationships']
    RELATIONSHIPS = [
        "count",
    ]

    def __init__(self, fake_response, parser_instance):
        # We want to have access to the parse instance mainly
        # to access fixtures if any
        self.parser_instance = parser_instance 

        # Remote controller for unique values - re.sub should return empty value.
        # After a mock value is created, and the mock value is checked against the instance's
        # current state of unique values - if it already exists, this instance attribute
        # would be a flag to remove this from the overall response to enforce uniqueness
        self._is_empty = False  

        # We need to keep track of the fake response that is being generated
        self.fake_response = fake_response

        # We store a list of all relationships specified for this endpoint
        self.relationships = []

        # A list of relationship targets - i.e. those on the right hand side of the
        # relationship syntax
        self.relationship_targets = []

        # This is the default duplication count - no duplication - we only create
        # one instance of the responses unless other specified by the `__mockcount`
        # property
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
    def handle_other_factory_method(attr, minimum, maximum):
        """
        This is a temporary static method, when there are more factory
        methods, we can move this to another class or find a way to maintain
        it in a scalable manner
        """
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
        
        # If `attr` isn't specified above, we need to raise an error
        raise ValueError('`%s` isn\'t a valid factory method.' % attr)

    def _replace_faker_attr(self, matchobj):
        """
        Callable used in re.sub to match, generate and replace the
        valid syntax found in the mock response specifications.
        """
        attr = matchobj.group(0).replace('<', '').replace('>', '')

        # Prepare template to handle quotes
        # For example, in situtations where the specification may
        # be "<first_name__from__users> <last_name__from__users>"
        # we want to be able to generate "John Doe" instead of "'John' 'Doe'"
        # so we create a template based on how it originally looked
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

        # 'fk' relationship fakes a 'Foreign Key' relationship but in actual
        # fact it just serves as a reference to an existing value
        if 'fk__' in attr:
            attr_map = [x.replace('"', '').replace("'", '') for x in attr.replace('fk__', '').split('.')]
            source_value = reduce(operator.getitem, attr_map, self._response_holder)
            if isinstance(source_value, str):
                return template.format(startswithquote, source_value, endswithquote)
            return source_value

        # We need to go through all the loaded fixtures to find the correct
        # values from the source file specified
        if '__from__' in attr:
            target, source = [x.replace('"', '').replace("'", '') for x in attr.split('__from__')]
            if self.parser_instance.fixture_data is not None:
                # Load up all the source values
                # e.g. for "<name__from__users>" we want to load up
                # all 'name' values retrieved from the 'users' fixture
                # into a store, essentially a list
                target_val_store = getattr(self, target + '_store', None)

                # Create a store if it doesn't exist yet
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

                # Store already exists, so if response is specified
                # to enforce uniqueness, we need to make use of the store to check
                # if not, we can just ignore it
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

        # If the response is not any of the special properties above
        # we will handle it below

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
            fake_val = validate_fake_val(fake_val, fake_func, minimum, maximum)
        except AttributeError:
            # Check other methods
            fake_val = self.handle_other_factory_method(attr, minimum, maximum)

        if is_unique:
            while True:
                if fake_val not in temp_state:
                    break
                fake_val = fake_func()
                fake_val = validate_fake_val(fake_val, fake_func, minimum, maximum)
            temp_state.append(fake_val)
            setattr(self, attr.strip("'") + '__temp_state', temp_state)

        if attr_copy in ['int', 'float']:
            return fake_val
        return template.format(startswithquote, fake_val, endswithquote)

    def _parse_syntax(self, raw):
        """
        Retrieves the syntax from the response and goes through each
        one to generate and replace it with mock values
        """
        raw = str(raw)  # treat the value as a string regardless of its actual data type
        has_syntax = re.findall(r'<(\^)?(fk__)?(\w+)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?>', raw, flags=re.DOTALL)

        if has_syntax:
            fake_val = re.sub(
                r'\'?\"?<(\^)?(fk__)?(\w+)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?(\:)?([0-9]*[.]?[0-9]+?)?>\'?\"?',
                self._replace_faker_attr,
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
    
    def _relationship_handler(self, source, relationship, target):
        handler = getattr(self, relationship)
        return handler(source, target)

    def count(self, source, target):
        """
        The 'count' relationship is used for listing endpoints where a specific attribute
        might hold the value to the number of instances of another attribute.
        """
        try:
            source_value = self._response_holder[source]
        except KeyError:
            # Source value hasn't been determined yet, we need
            # to generate the source value first
            raw = self.fake_response[source]
            source_value = self._parse_syntax(raw)
        if isinstance(source_value, str):
            source_value = int(source_value)
        target = self.fake_response[target]
        values = []
        for _ in range(source_value):
            self._is_empty = False  # Remote state for re.sub to switch in case it hits a None value
            mock_value = self._parse_syntax(target)
            mock_value = str(mock_value)  # Treat the value as a string regardless of its actual data type
            _target = mock_value[1:-1]  # Remove extra quotation
            _target = _target.replace("'", '"')

            try:
                mock_value = json.loads(_target)
            except:
                mock_value = _target

            # If uniqueness is specified and this mock value isn't
            # in the store yet, then we can append it to the results
            if not self._is_empty:
                values.append(mock_value)
        return values

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
