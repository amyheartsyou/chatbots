
from chatbots.handler import MessageHandler
from chatbots.clients import DiscordClient
from chatbots.clients import CLTClient
from chatbots import settings


RESPONSES = {
   r'\$cat': ['yeah, that mad black cat attacked that plastic bag'],
}


if __name__ == '__main__':
    handler = MessageHandler()
    handler.add_responses(RESPONSES)
    client = CLTClient(None, handler)
    client.run(settings.BOT_TOKEN)
