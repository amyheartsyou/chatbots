import argparse
import logging
import os

from chatbots import clients
import credentials
import handler
import responses
import settings
from model import TreasurePersistor


parser = argparse.ArgumentParser(description="TreasureBotParser")
parser.add_argument('mode', type=str)

MODE_CLT = 'cli'
MODE_DISCORD = 'discord'


def config_logging(cwd, level):
    filename = os.path.join(cwd, settings.LOG_FILE)
    if not os.path.exists(filename):
        open(filename, 'a').close()

    logging.basicConfig(
        format=settings.LOG_FORMAT,
        filename=filename,
        level=level
    )


def get_message_handler():
    message_handler = handler.MessageHandler()
    message_handler.add_responses(responses.RESPONSES)
    message_handler.add_user_responses(
        settings.AMY_ID,
        responses.AMY_RESPONSES
    )
    return message_handler


def run_client(client_class, cwd):
    filename = os.path.join(cwd, settings.DB_NAME)
    with TreasurePersistor(filename) as persistor:
        command_handler = handler.CommandHandler(persistor)
        message_handler = get_message_handler()

        client = client_class(command_handler, message_handler)
        client.run(credentials.BOT_TOKEN)


if __name__ == '__main__':
    args = parser.parse_args()

    cwd = os.path.dirname(os.path.realpath(__file__))
    config_logging(cwd, logging.INFO)

    if args.mode == MODE_DISCORD:
        client_class = clients.DiscordClient
    elif args.mode == MODE_CLT:
        client_class = clients.CLTClient
    else:
        raise Exception(f"Invalid Client: {args.mode}")

    run_client(client_class, cwd)
