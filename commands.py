import re

from chatbots import settings

# 300 cp
COIN_PATTERN = re.compile(r'(?P<quantity>\d+) (?P<name>\wp)')

# 2 x Jade (50 gp)
LOOT_PATTERN = re.compile(
    r'(?:(?P<quantity>\d+) x )?'
    r'(?P<name>[\w ]+(?: \(\w+\))?) '
    r'\((?P<value>[\.\d]+) (?P<unit>\wp)\)'
)

# 2 x Widget (rare, dmg 99)
ITEM_PATTERN = re.compile(
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

'''
 Iron Dice (pair) (25 gp),
 Potion of Resistance (radiant) (uncommon, dmg 188)
 add $help
 '''


class Command:

    def __init__(self, message):
        self.action = None
        self.data = None
        self.errors = []

        self._item_parsers = [
            self.parse_coin,
            self.parse_rare,
            self.parse_spell,
            self.parse_loot,
        ]

        self.parse(message)

    def parse(self, message):
        parts = re.split(
            r'^(\w+)',
            message[len(settings.COMMAND_PREFIX):].strip()
        )
        command = parts[1].lower()
        arguments = parts[2].strip()

        if command == 'add':
            self.action = 'add_treasure'
            self.data, self.errors = self.parse_add_command(arguments)
        elif command in ['list', 'show']:
            self.action = 'list_treasure'
            self.data = self.parse_query(arguments)
            # self.treasure_type = self.parse_type(arguments)
        elif command in ['delete', 'drop', 'remove', 'forget']:
            self.action = 'remove_treasure'
            self.data = self.parse_query(arguments)
            # self.treasure_type = self.parse_type(arguments)
        elif command == 'split':
            self.action = 'split'
            self.data = self.parse_split(arguments)
        elif command == 'spend':
            self.action = 'spend_coin'
            self.data = self.parse_spend(arguments)
        elif command.startswith('shh'):
            self.action = 'silence'
            self.data = self.parse_shh(arguments)
        elif command == 'talk':
            self.action = 'unsilence'
        elif command == 'help':
            self.action = 'help'

    def parse_spend(self, arguments):
        pairs = []
        parts = arguments.split()
        if len(parts) % 2 != 0:
            self.errors.append('Unbalanced arguments')
            return
        for idx in range(0, len(parts), 2):
            try:
                quantity = int(parts[idx])
            except ValueError:
                self.errors.append(f"{parts[idx]} isn't a number.")
                return
            if parts[idx+1] not in settings.VALUES:
                self.errors.append(f"{parts[idx+1]} isn't a coin type.")
                return
            pairs.append((quantity, parts[idx+1]))
        return pairs

    def parse_split(self, arguments):
        return arguments.split()

    def parse_query(self, query):
        parsed_args = []
        for query_arg in query.split(','):
            query_arg = query_arg.strip()
            if query_arg.upper().rstrip('S') in settings.GROUPS:
                parsed_args.append(query_arg.upper().rstrip('S'))
            elif query_arg.lower() in settings.VALUES:
                parsed_args.append(query_arg.lower())
            else:
                parsed_args.append(query_arg.capitalize())

        return parsed_args

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

    def parse_type(self, message):
        treasure_type = message.strip().upper().rstrip('S')
        if treasure_type == 'SPELL':
            treasure_type = 'SCROLL'
        return treasure_type

    def parse_item(self, message, pattern):
        match = pattern.match(message)
        if match is None:
            return

        item = match.groupdict()
        item['quantity'] = int(item['quantity'] or 1)
        return item

    def parse_coin(self, message):
        item = self.parse_item(message, COIN_PATTERN)
        if item:
            item['type'] = 'COIN'
            item['value'] = settings.VALUES[item['name']]
            return item

    def parse_rare(self, message):
        item = self.parse_item(message, ITEM_PATTERN)
        if item:
            item['quantity'] = int(item.get('quantity') or 1)
            item['type'] = 'ITEM'
            return item

    def parse_loot(self, message):
        item = self.parse_item(message, LOOT_PATTERN)
        if item:
            item['type'] = (
                'GEM' if item['name'].lower() in settings.GEMS else 'LOOT')
            item['value'] = int(item['value']) * settings.VALUES[item['unit']]
            item['quantity'] = int(item.get('quantity') or 1)
            del item['unit']
            return item

    def parse_spell(self, message):
        item = self.parse_item(message, SPELL_PATTERN)
        if item:
            item['type'] = 'SCROLL'
            return item

    def parse_shh(self, message):
        try:
            return int(message)
        except ValueError:
            self.errors.append(f"{message} isn't a duration")
