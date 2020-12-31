import argparse
import logging

from chatbots import clients
from chatbots import handler
from chatbots import responses
from chatbots import settings
from chatbots.model import TreasurePersistor


parser = argparse.ArgumentParser(description="TreasureBotParser")
parser.add_argument('mode', type=str)

MODE_CLT = 'clt'
MODE_DISCORD = 'discord'


def config_logging(level):
    logging.basicConfig(
        format=settings.LOG_FORMAT,
        filename=settings.LOG_FILE,
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


def run_client(client_class):
    with TreasurePersistor(settings.DB_NAME) as persistor:
        command_handler = handler.CommandHandler(persistor)
        message_handler = get_message_handler()

        client = client_class(command_handler, message_handler)
        client.run(settings.BOT_TOKEN)


if __name__ == '__main__':
    config_logging(logging.INFO)
    args = parser.parse_args()
    if args.mode == MODE_DISCORD:
        client_class = clients.DiscordClient
    elif args.mode == MODE_CLT:
        client_class = clients.CLTClient
    else:
        raise Exception(f"Invalid Client: {args.mode}")

    run_client(client_class)
