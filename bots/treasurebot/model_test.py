import unittest

from chatbots.bots.treasurebot import model
from chatbots.bots.treasurebot import test_data


TEST_DB_PATH = ':memory:'


class TreasurePersistorTest(unittest.TestCase):

    def tearDown(self):
        model.Treasure.drop_table()

    def assertItemMatches(self, expected, actual):
        self.assertEqual(expected["name"], actual.name)
        self.assertEqual(expected["type"], actual.type)
        self.assertEqual(expected.get("value", 0), actual.value)
        self.assertEqual(expected.get("quantity", 1), actual.quantity)
        self.assertEqual(expected.get("description", ""), actual.description)

    def createRecords(self, persistor, items):
        for item in items:
            record = persistor.add_treasure(item)
            self.assertGreater(record.id, 0)
        return dict((item["name"], item) for item in items)

    def testAddNewTreasure(self):
        treasure = {
            'quantity': 10,
            'name': 'treasure',
            'value': 100,
            'type': 'LOOT',
        }
        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            record = persistor.add_treasure(treasure)

        self.assertItemMatches(treasure, record)

    def test_add_existing_treasure(self):
        treasure = {
            'name': 'treasure_name',
            'value': 60,
            'type': 'LOOT',
        }

        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            self.createRecords(persistor, [treasure])
            record = persistor.add_treasure(treasure)

        self.assertEqual('treasure_name', record.name)
        self.assertEqual(2, record.quantity)
        self.assertEqual(60, record.value)
        self.assertEqual('LOOT', record.type)

    def test_get_all_treasure(self):

        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            expected = self.createRecords(persistor, test_data.TREASURE)
            actual = list(persistor.get_treasure('ALL'))

        self.assertEqual(len(expected), len(actual))
        for item in actual:
            self.assertItemMatches(expected[item.name], item)

    def test_get_by_type(self):
        treasure_types = ['COIN', 'LOOT', 'ITEM', 'GEM']

        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            expected = self.createRecords(persistor, test_data.TREASURE)

            for treasure_type in treasure_types:
                with self.subTest():
                    actual = list(persistor.get_treasure(treasure_type))
                    self.assertGreaterEqual(len(actual), 1)
                    exptected_quantity = sum(
                        1 for item in expected.values()
                        if item['type'] == treasure_type
                    )
                    self.assertEqual(exptected_quantity, len(actual))

                    for item in actual:
                        self.assertEqual(treasure_type, item.type)

    def test_delete_some_coin(self):
        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            expected = self.createRecords(persistor, test_data.TREASURE)
            persistor.remove_treasure('cp', quantity=50)

            actual = model.Treasure.get(name='cp', type='COIN')

        self.assertEqual('cp', actual.name)
        self.assertEqual(expected['cp']['quantity']-50, actual.quantity)

    def test_delete_all_coin(self):
        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            self.createRecords(persistor, test_data.TREASURE)
            persistor.remove_treasure('cp')

            actual = model.Treasure.get(
                model.Treasure.name == 'cp',
                model.Treasure.type == 'COIN',
            )
        self.assertEqual('cp', actual.name)
        self.assertEqual(0, actual.quantity)

    def test_delete_some_item(self):
        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            expected = self.createRecords(persistor, test_data.TREASURE)
            persistor.remove_treasure('chrysoprase', quantity=1)

            actual = model.Treasure.get(name='chrysoprase', type='GEM')

        self.assertEqual('chrysoprase', actual.name)
        self.assertEqual(
            expected['chrysoprase']['quantity']-1,
            actual.quantity
        )

    def test_delete_all_item(self):
        with model.TreasurePersistor(TEST_DB_PATH) as persistor:
            self.createRecords(persistor, test_data.TREASURE)
            persistor.remove_treasure('chrysoprase')

            with self.assertRaises(model.Treasure.DoesNotExist):
                model.Treasure.get(name='chrysoprase', type='GEM')


if __name__ == '__main__':
    unittest.main()
