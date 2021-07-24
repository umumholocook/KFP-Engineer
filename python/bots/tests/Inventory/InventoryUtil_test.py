from common.InventoryUtil import InventoryUtil
from common.KFP_DB import KfpDb
from common.MemberUtil import MemberUtil

class TestInventoryUtil():
    def setup_method(self, method):
        self.database = KfpDb()
    
    def teardown_method(self, method):
        self.database.teardown()
    
    def test_getInventory_empty(self):
        inventory = InventoryUtil.getAllItemsBelongToUser(1, 1)
        assert len(inventory) == 0

    def test_findItem_success(self):
        item1 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        result = InventoryUtil.searchItem(guild_id=1, item_name="hello")
        assert result == item1

    def test_addItemToDb_success(self):
        item1 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        item2 = InventoryUtil.createItem(guild_id=1, item_name="hey")
        items = InventoryUtil.ListAllItem(guild_id=1)
        assert items == [item1, item2]

    def test_addItemToDb_failed_samename(self):
        item1 =InventoryUtil.createItem(guild_id=1, item_name="hello")
        item2 = InventoryUtil.createItem(guild_id=1, item_name="hello")
        items = InventoryUtil.ListAllItem(guild_id=1)
        assert len(items) == 1 and item2 == -1

    def test_addItemTOShop_success(self):
        InventoryUtil.createItem(guild_id=1, item_name="hello")
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result == [shopItem1]

    def test_addItemTOShop_failed_noitem(self):
        InventoryUtil.createItem(guild_id=1, item_name="hello")
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        InventoryUtil.addItemToShop(guild_id=1, item_name="he", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result == []

    def test_addItemTOShop_success_addAmount(self):
        InventoryUtil.createItem(guild_id=1, item_name="hello")
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result[0].amount == 20 and len(result) == 1

    def test_findShopItem_success(self):
        InventoryUtil.createItem(guild_id=1, item_name="hello")
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.findShopItem(guild_id=1, item_id=shopItem1.item_id)
        assert result == shopItem1

    def test_findShopItem_failed(self):
        InventoryUtil.createItem(guild_id=1, item_name="hello")
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.findShopItem(guild_id=1, item_id=5)
        assert result == -1

    def test_buyItem_empty(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert len(itemList) == 0

    def test_buyItem_success(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        InventoryUtil.createItem(guild_id=1, item_name="hello", level_required=0, price=10)
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=shopItem1.id, count=2)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert itemList[0].user_id == 123 and itemList[0].item == shopItem1.item

    def test_buyItems_success(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        InventoryUtil.createItem(guild_id=1, item_name="hello", level_required=0, price=10)
        InventoryUtil.createItem(guild_id=1, item_name="hey")
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        shopItem2 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=shopItem1.id, count=2)
        InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=shopItem2.id, count=4)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert len(itemList) == 2

    def test_buyItem_failed_noProduct(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        InventoryUtil.createItem(guild_id=1, item_name="hello", level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=5, count=2)
        assert result == -1

    def test_buyItem_failed_noMoney(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=10)
        InventoryUtil.createItem(guild_id=1, item_name="hello", level_required=0, price=100)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=shopItem1.id, count=2)
        assert result == -2

    def test_buyItem_failed_notEnoughSupply(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        InventoryUtil.createItem(guild_id=1, item_name="hello", level_required=0, price=10)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=1)
        result = InventoryUtil.buyItem(guild_id=1, user_id=123, item_id=shopItem1.id, count=2)
        assert result == -3