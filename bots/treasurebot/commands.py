import re

import settings

# 300 cp
COIN_PATTERN = re.compile(r'(?P<quantity>\d+) (?P<name>\wp)')

# 2 x Jade (50 gp)
LOOT_PATTERN = re.compile(
    r'(?:(?P<quantity>\d+) x )?'
    r'(?P<name>[\w ]+(?: \(\w+\))?) '
    r'\((?P<value>[\.\d]+) (?P<unit>\wp)\)'
)

# 2 x Widget (rare, dmg 99)
RARE_PATTERN = re.compile(
    r'(?:(?P<quantity>\d+) x )?'
    r'(?P<name>[^(]+(?: \(\w+\))?) '
    r'\(\w+, dmg \d+\)'
)

# 5 X Spell Scroll (Merton)
SPELL_PATTERN = re.compile(
    r'(?:(?P<quantity>\d+) x )?'
    r'Spell Scroll '
    r'\((?P<name>[\w ]+)\)'
)

# Splits on commas that are not inside parenthesis.
SPLIT_PATTERN = re.compile(r',(?![^\(]*\)) ?')


class Command:

    def __init__(self, message):
        self._item_parsers = [
            self._parse_coin,
            self._parse_rare,
            self._parse_spell,
            self._parse_loot,
        ]

        self.action, self.data, self.errors = self.parse(message)

    def parse(self, message):
        action = None
        data = None
        errors = []

        parts = re.split(
            r'^(\w+)',
            message[len(settings.COMMAND_PREFIX):].strip()
        )
        command = parts[1].lower()
        arguments = parts[2].strip()

        if command == 'add':
            action = 'add_treasure'
            data, errors = self.parse_add_command(arguments)
        elif command in ['list', 'show']:
            action = 'list_treasure'
            data = self.parse_query(arguments)
        elif command in ['delete', 'drop', 'remove', 'forget']:
            action = 'remove_treasure'
            data = self.parse_query(arguments)
        elif command == 'split':
            action = 'split'
            data = self.parse_split(arguments)
        elif command == 'spend':
            action = 'spend_coin'
            data, errors = self.parse_spend(arguments)
        elif command.startswith('shh'):
            action = 'silence'
            data, errors = self.parse_shh(arguments)
        elif command == 'talk':
            action = 'unsilence'
        elif command == 'help':
            action = 'help'

        return action, data, errors

    def parse_add_command(self, message):
        entries = SPLIT_PATTERN.split(message)
        items = []
        errors = []

        for entry in entries:
            for item_parser in self._item_parsers:
                item = item_parser(entry)
                if item:
                    items.append(item)
                    break
            else:
                errors.append(entry)

        return items, errors

    def parse_query(self, query):
        parsed_args = []
        for query_arg in query.split(','):
            query_arg = query_arg.strip()
            if query_arg.upper().rstrip('S') in settings.GROUPS:
                parsed_args.append(query_arg.upper().rstrip('S'))
            else:
                parsed_args.append(query_arg.lower())

        return parsed_args

    def parse_split(self, arguments):
        return arguments.split()

    def parse_spend(self, arguments):
        pairs = []
        errors = []

        parts = arguments.split()
        if len(parts) % 2 != 0:
            errors.append('Unbalanced arguments')
            return
        for idx in range(0, len(parts), 2):
            try:
                quantity = int(parts[idx])
            except ValueError:
                errors.append(f"{parts[idx]} isn't a number.")
                return
            if parts[idx+1] not in settings.VALUES:
                errors.append(f"{parts[idx+1]} isn't a coin type.")
                return
            pairs.append((quantity, parts[idx+1]))

        return pairs, errors

    def parse_shh(self, message):
        data = None
        errors = []
        try:
            data = int(message)
        except ValueError:
            errors.append(f"{message} isn't a duration")

        return data, errors

    def _parse_item(self, message, pattern):
        match = pattern.match(message)
        if match is None:
            return

        item = match.groupdict()
        item['quantity'] = int(item['quantity'] or 1)
        item['name'] = item['name'].lower()
        return item

    def _parse_coin(self, message):
        item = self._parse_item(message, COIN_PATTERN)
        if item:
            item['type'] = 'COIN'
            item['value'] = settings.VALUES[item['name']]
            return item

    def _parse_loot(self, message):
        item = self._parse_item(message, LOOT_PATTERN)
        if item:
            item['type'] = (
                'GEM' if item['name'].lower() in settings.GEMS else 'LOOT')
            item['value'] = int(item['value']) * settings.VALUES[item['unit']]
            del item['unit']
            return item

    def _parse_rare(self, message):
        item = self._parse_item(message, RARE_PATTERN)
        if item:
            item['type'] = 'ITEM'
            return item

    def _parse_spell(self, message):
        item = self._parse_item(message, SPELL_PATTERN)
        if item:
            item['type'] = 'SCROLL'
            return item

    def __str__(self):
        return (
            "<Command: {"
            f"action: {self.action}, "
            f"data: {self.data}, "
            f"errors: {self.errors}"
            "}>"
        )
