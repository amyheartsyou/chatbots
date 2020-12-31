import os
import datetime
import re
import random

from chatbots import settings

SHH_FILE = 'shh'


class CommandHandler:

    def __init__(self, persistor):
        self.persistor = persistor

    def handle(self, command):
        if command.errors:
            return f'Error: {", ".join(command.errors)}'

        return getattr(self, command.action, lambda x: None)(command)

    def add_treasure(self, command):
        added = ["Added: "]
        for item in command.data:
            self.persistor.add_treasure(item)
            added.append(item['name'])
        return ", ".join(added)

    def list_treasure(self, command):
        output = ["Currently held treasure:"]
        for item in command.data:
            for result in list(
                    self.persistor.get_treasure(item)):
                if result.quantity > 0:
                    output.append(
                        f'{result.quantity} x '
                        f'{result.name} '
                        f'({round(result.value, 2)} gp)'
                    )
        return '\n'.join(output)

    def remove_treasure(self, command):
        print(command.data)
        for item in list(command.data):
            self.persistor.remove_treasure(item)
        return 'Dropped.'

    def split(self, command):
        try:
            return float(command.data[0]) / float(command.data[1])
        except ValueError:
            return 'Unsplittable values... fool.'

    def spend_coin(self, command):
        for quantity, name in command.data:
            result = list(self.persistor.get_treasure(name))
            if quantity > result[0].quantity:
                return f'Not enough {name}.'
            self.persistor.remove_treasure(name, quantity=quantity)
        return 'Spent.'

    def silence(self, command):
        end = datetime.datetime.now() + datetime.timedelta(minutes=command.data)
        with open(settings.SHUSH_FILE, "w+") as handle:
            handle.write(end.strftime('%c'))

    def unsilence(self, _):
        os.remove(settings.SHUSH_FILE)

    def help(self, _):
        return '$add, $list, $drop, $split, $shh, $talk, $help'


class MessageHandler:

    def __init__(self):
        self.responses = {}
        self.user_responses = {}

    def add_responses(self, responses):
        for key in responses:
            self.responses[key] = responses[key]

    def add_user_responses(self, user_id, responses):
        if user_id not in self.user_responses:
            self.user_responses[user_id] = {}

        for key in responses:
            self.user_responses[user_id][key] = responses[key]

    def handle_user_message(self, author, message):
        if author in self.user_responses:
            return self.user_responses[author].get(message.lower())

    def handle_message(self, message):
        for key, responses in self.responses.items():
            if re.search(key, message.lower()):
                idx = random.randint(0, len(responses)-1)
                return self.responses[key][idx]

    def is_shushed(self):
        try:
            with open(settings.SHUSH_FILE) as handle:
                end = datetime.datetime.strptime(handle.read(), '%c')
                if end > datetime.datetime.now():
                    return True
                else:
                    os.remove(settings.SHUSH_FILE)
        except FileNotFoundError:
            pass

    def handle(self, author, message):
        if self.is_shushed():
            return

        return (self.handle_user_message(author, message) or
                self.handle_message(message))
