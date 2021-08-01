from common.RPGUtil.ItemType import ItemType
from common.KFP_DB import KfpDb
from common.RPGUtil.ItemUtil import ItemUtil

class TestItemUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")

    def teardown_method(self, method):
        self.database.teardown()

    def test_searchItem_success(self):
        item1 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2)
        result = ItemUtil.searchItem(guild_id=1, item_name="hello")
        assert result == item1

    def test_searchItem_fail(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2)
        result = ItemUtil.searchItem(guild_id=1, item_name="he")
        assert result == None

    def test_createItem_success(self):
        item1 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2)
        result = ItemUtil.ListAllItem(guild_id=1)
        assert len(result) == 1 and result[0] == item1

    def test_createItem_failed_itemExist(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2)
        result = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2)
        assert result == -1

    def test_deleteItem_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2, level_required=0, price=1)
        ItemUtil.deleteItem(guild_id=1, item_name="hello")
        result = ItemUtil.ListAllItem(guild_id=1)
        assert result == []

    def test_deleteItem_failed_noItem(self):
        ItemUtil.deleteItem(guild_id=1, item_name="hello")
        result = ItemUtil.ListAllItem(guild_id=1)
        assert result == []

    def test_deleteItems_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=1, buff_value=-1, buff_round=2, level_required=0, price=1)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=2, buff_value=10, buff_round=3, level_required=0, price=1)
        ItemUtil.createItem(guild_id=1, item_name="heap", item_type=ItemType.STATUS, buff_type=2, buff_value=10, buff_round=3, level_required=0, price=1)
        ItemUtil.createItem(guild_id=1, item_name="hot", item_type=ItemType.STATUS, buff_type=2, buff_value=10, buff_round=3, level_required=0, price=1)
        ItemUtil.deleteItems(guild_id=1)
        result = ItemUtil.ListAllItem(guild_id=1)
        assert result == []

    def test_deleteItems_failed_noItem(self):
        ItemUtil.deleteItems(guild_id=1)
        result = ItemUtil.ListAllItem(guild_id=1)
        assert result == []
