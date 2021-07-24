from common.InventoryUtil import InventoryUtil
from common.KFP_DB import KfpDb

class TestInventoryUtil():
    def setup_method(self, method):
        self.database = KfpDb()
    
    def teardown_method(self, method):
        self.database.teardown()
    
    def test_getInventory_empty(self):
        inventory = InventoryUtil.getAllItemsBelongToUser(1, 1)
        assert len(inventory) == 0

    def test_addItemToDb(self):
        item1 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        item2 = InventoryUtil.createItem(guild_id=1, item_name="hey")
        items = InventoryUtil.ListAllItem(guild_id=1)
        assert items == [item1, item2]

    def test_addItemTOShop_success(self):
        item1 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        item2 = InventoryUtil.createItem(guild_id=1, item_name="hey")
        result = InventoryUtil.addItemToShop(guild_id=1, item_name="hey",amount=10)
        assert 1 == 1

    def test_addItemTOShop_failed(self):
        item1 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        item2 = InventoryUtil.createItem(guild_id=1, item_name="hey")
        result = InventoryUtil.addItemToShop(guild_id=1, item_name="hey",amount=10)
        assert -1 == -1