import peewee

from chatbots import settings


db = peewee.SqliteDatabase(None)


class Treasure(peewee.Model):
    id = peewee.AutoField()
    quantity = peewee.IntegerField(default=1)
    name = peewee.CharField()
    value = peewee.FloatField(default=0)
    description = peewee.TextField(default='')
    type = peewee.CharField(
        choices=[(group, group) for group in settings.GROUPS]
    )

    class Meta:
        database = db

    def __str__(self):
        return (f'id: {self.id}, quantity: {self.quantity}, name: '
                f'{self.name}, value: {self.value}, type: {self.type}')


class TreasurePersistor:

    def __init__(self, db_path):
        self.db_path = db_path
        self.db = None

    def __enter__(self):
        self.db = peewee.SqliteDatabase(self.db_path)
        self.db.bind([Treasure], bind_refs=False, bind_backrefs=False)
        self.db.connect()
        self.db.create_tables([Treasure])
        self.initialize_coins()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def initialize_coins(self):
        missing = []
        coins = (
            t.name for t in Treasure.select().where(Treasure.type == 'COIN')
        )
        for coin in settings.VALUES:
            if coin not in coins:
                missing.append(coin)

        if not missing:
            return

        for name in missing:
            record = Treasure(
                name=name,
                value=settings.VALUES[name],
                type='COIN',
                quantity=0,
            )
            record.save()

    def add_treasure(self, treasure_data):
        record = Treasure(**treasure_data)
        try:
            existing = Treasure.get(
                Treasure.name == record.name,
                Treasure.value == record.value,
                Treasure.type == record.type,
            )
        except Treasure.DoesNotExist:
            record.save()
            return record
        else:
            existing.quantity += record.quantity
            existing.save()
            return existing

    def get_treasure(self, treasure_filter):
        if treasure_filter == 'ALL':
            return Treasure.select()
        elif treasure_filter in settings.GROUPS:
            return Treasure.select().where(Treasure.type == treasure_filter)
        else:
            return Treasure.select().where(Treasure.name == treasure_filter)

    def remove_treasure(self, identifier, quantity=None):
        if identifier in settings.GROUPS:
            results = Treasure.select().where(Treasure.type == identifier)
        else:
            results = Treasure.select().where(Treasure.name == identifier)

        results = list(results)

        for result in results:
            if quantity is None or quantity > result.quantity:
                result.quantity = 0
            else:
                result.quantity -= quantity

            if result.quantity > 0 or result.type == 'COIN':
                result.save()
            else:
                result.delete_instance()
