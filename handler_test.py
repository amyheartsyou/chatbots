import unittest


from chatbots import responses
from chatbots import settings
from chatbots.handler import MessageHandler


class CommandHandlerTest(unittest.TestCase):
    """"""


class MessageHandlerTest(unittest.TestCase):

    def testHandleUserMessage(self):
        handler = MessageHandler()
        handler.add_user_responses(settings.AMY_ID, responses.AMY_RESPONSES)
        response = handler.handle(settings.AMY_ID, '❤️')
        self.assertEqual("TreasureBot ❤️'s Amy.", response)

    def testHandleMessage(self):
        handler = MessageHandler()
        handler.add_user_responses(settings.AMY_ID, responses.AMY_RESPONSES)
        handler.add_responses(responses.RESPONSES)
        response = handler.handle(123456789, '|❤️|')
        self.assertEqual("💩", response)

    def testHandleUnrecognized(self):
        handler = MessageHandler()
        handler.add_responses(responses.RESPONSES)
        response = handler.handle(10000, 'xyz')
        self.assertIsNone(response)


if __name__ == '__main__':
    unittest.main()
