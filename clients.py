
import logging

import discord

from chatbots import commands
from chatbots import settings


AMY = 'Amy'
AMY_COMMAND = '`AMY'
USER_COMMAND = '`'
AUTHOR_NAME = 'You'


class Client:

    def __init__(self, command_handler, message_handler):
        super().__init__()
        self.command_handler = command_handler
        self.message_handler = message_handler

    def handle_message(self, author, message):
        message = message.strip()
        if self.command_handler and message.startswith(settings.COMMAND_PREFIX):
            command = commands.Command(message)
            response = self.command_handler.handle(command)
        else:
            response = self.message_handler.handle(author, message)
        return response


class DiscordClient(Client, discord.Client):

    def __init__(self, command_handler, message_handler):
        logging.info('Intializing Discord Client')
        super().__init__(command_handler, message_handler)

    async def on_ready(self):
        logging.info(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author.id == settings.BOT_ID:
            return

        logging.info(
            f'Received message from {message.guild.name}:'
            f'{message.channel.name}:'
            f'{message.author.name} ({message.author.id}) -- '
            f'"{message.content}"')

        response = self.handle_message(message.author.id, message.content)

        if response:
            await message.channel.send(response)


class CLTClient(Client):
    def __init__(self, command_handler, message_handler):
        print("Initializing CLT Client")
        super().__init__(command_handler, message_handler)
        self.author = AUTHOR_NAME

    def handle_user_switch(self, content):
        if content.startswith(AMY_COMMAND):
            self.author = AMY
            content = content[len(AMY_COMMAND):]
        elif content.startswith(USER_COMMAND):
            self.author = AUTHOR_NAME
            content = content[len(USER_COMMAND):]
        return content

    def run(self, _):
        while True:
            content = input(f'{self.author}: ')

            content = self.handle_user_switch(content)

            if self.author == AMY:
                author_id = settings.AMY_ID
            else:
                author_id = 100

            response = self.handle_message(author_id, content.strip())

            if response:
                print('TreasureBot:', response)
