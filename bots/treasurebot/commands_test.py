import unittest

from chatbots.bots.treasurebot import commands


class HandlerTest(unittest.TestCase):

    def testParseAddCoin(self):
        message = '$add 300 cp, 900 sp'
        expected = [
            {"quantity": 300, "name": 'cp', "type": 'COIN', "value": 0.01},
            {"quantity": 900, "name": 'sp', "type": 'COIN', "value": 0.1},
        ]
        command = commands.Command(message)
        self.assertEqual('add_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testParseAddGems(self):
        message = (
            '$add '
            'Jade (50 gp), '
            '2 x Citrine (500 sp)'
        )
        expected = [
            {"quantity": 1, "type": 'GEM', "value": 50.0, "name": "jade"},
            {"quantity": 2, "type": 'GEM', "value": 50.0, "name": "citrine"},
        ]
        command = commands.Command(message)
        self.assertEqual('add_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testParseAddLoot(self):
        message = (
            '$add '
            'Treas 1 (24 gp), '
            'Treas 2 (60 gp), '
            '3 x Treas 3 (77 gp)'
        )
        expected = [
            {"quantity": 1, "name": "treas 1", "type": 'LOOT', "value": 24.0},
            {"quantity": 1, "name": "treas 2", "type": 'LOOT', "value": 60.0},
            {"quantity": 3, "name": "treas 3", "type": 'LOOT', "value": 77.0},
        ]
        command = commands.Command(message)
        self.assertEqual('add_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testParseAddItem(self):
        message = (
            '$add '
            'Item 1 (rare, dmg 191), '
            '2 x Item 2 (rare, dmg 555)'
        )
        expected = [
            {"quantity": 1, "name": 'item 1', "type": "ITEM"},
            {"quantity": 2, "name": 'item 2', "type": "ITEM"},
        ]
        command = commands.Command(message)
        self.assertEqual('add_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testParseAddSpell(self):
        message = (
            '$add '
            'Spell Scroll (Spell 1) (uncommon, dmg 200), '
            '2 x Spell Scroll (Spell 2) (rare, dmg 343)'
        )
        expected = [
            {"quantity": 1, "name": 'spell 1', "type": "SCROLL"},
            {"quantity": 2, "name": 'spell 2', "type": "SCROLL"},
        ]
        command = commands.Command(message)
        self.assertEqual('add_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testDropLoot(self):
        message = (
            '$drop '
            'Treas 1,'
            '2 x Treas 2'
        )
        expected = ['treas 1', '2 x treas 2']
        command = commands.Command(message)
        self.assertEqual('remove_treasure', command.action)
        self.assertEqual(0, len(command.errors))
        self.assertEqual(expected, command.data)

    def testParseList(self):
        messages = [
            '$list coins',
            '$drop scroll'
        ]
        expecteds = [
            {'action': 'list_treasure', 'type': 'COIN'},
            {'action': 'remove_treasure', 'type': 'SCROLL'},
        ]

        for message, expected in zip(messages, expecteds):
            with self.subTest():
                actual = commands.Command(message)
                self.assertEqual(expected['action'], actual.action)
                self.assertEqual([expected['type']], actual.data)


if __name__ == '__main__':
    unittest.main()
