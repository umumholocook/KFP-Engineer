from common.RPGUtil.ItemType import ItemType
from common.RPGUtil.Buff import Buff, BuffType
from common.RPGUtil.InventoryUtil import InventoryUtil, ErrorCode
from common.KFP_DB import KfpDb
from common.MemberUtil import MemberUtil
from common.RPGUtil.ItemUtil import ItemUtil

class TestInventoryUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
    
    def teardown_method(self, method):
        self.database.teardown()
    
    def test_getInventory_empty(self):
        inventory = InventoryUtil.getAllItemsBelongToUser(1, 1)
        assert len(inventory) == 0

    def test_buffTypeStorage_success(self):
        item = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=30, buff_round=3)
        item_buff:Buff = item.buff
        assert item_buff.buff_type == BuffType.ATTACK
        assert item_buff.buff_value == 30
        assert item_buff.buff_round == 3

    def test_buffTypeStorageRead_success(self):
        item = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=30, buff_round=3)
        item_from_db = ItemUtil.ListAllItem(guild_id=1)[0]
        item_buff:Buff = item_from_db.buff
        assert item_buff.buff_type == BuffType.ATTACK
        assert item_buff.buff_value == 30
        assert item_buff.buff_round == 3

    def test_addItemToItemdb_success(self):
        item1 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        item2 = ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        items = ItemUtil.ListAllItem(guild_id=1)
        assert items == [item1, item2]

    def test_addItemToItemdb_failed_samename(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        item2 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        items = ItemUtil.ListAllItem(guild_id=1)
        assert len(items) == 1 and item2 == -1

    def test_addItemTOShop_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result == [shopItem1]

    def test_addItemTOShop_failed_noitem(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        InventoryUtil.addItemToShop(guild_id=1, item_name="he", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result == []

    def test_addItemTOShop_success_addAmount(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result[0].amount == 20 and len(result) == 1

    def test_addItemTOShop_failed_addAmount(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        InventoryUtil.addItemToShop(guild_id=1, item_name="he", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="he", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result == []

    def test_addItemTOShop_failed_unlimitedSupply(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=-1)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert result[0].amount == -1

    def test_addItemTOShop_failed_limitedToUnlimited(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        shopitem = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=-1)
        assert result == -3 and shopitem.amount == 10

    def test_findShopItem_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.findShopItem(guild_id=1, item=shopItem1.item)
        assert result == shopItem1

    def test_findShopItem_failed(self):
        item1 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        result = InventoryUtil.findShopItem(guild_id=1, item=item1)
        assert result == None

    def test_deleteShopItem(self):
        item1 = ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=100)
        list = InventoryUtil.ShopMenu(guild_id=1)
        assert len(list) == 2
        InventoryUtil.deleteShopItem(guild_id=1, item=item1)
        list = InventoryUtil.ShopMenu(guild_id=1)
        assert len(list) == 1

    def test_deleteShopItems(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=100)
        list = InventoryUtil.ShopMenu(guild_id=1)
        assert len(list) == 2
        InventoryUtil.deleteShopItems(guild_id=1)
        list = InventoryUtil.ShopMenu(guild_id=1)
        assert len(list) == 0

    def test_getAllItemsBelongToUser_empty(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert len(itemList) == 0

    def test_buyShopitem_success(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=2)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert itemList[0].user_id == 123 and itemList[0].item == shopItem1.item

    def test_buyShopitem_success_shopItemchangeHidden(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=500)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=1)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=10)
        InventoryUtil.checkZeroAmount(guild_id=1)
        result = InventoryUtil.ShopMenu(guild_id=1)
        assert len(result) == 0 and result == []

    def test_buyShopitems_success(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=500)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3, level_required=0, price=10)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        shopItem2 = InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=2)
        InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hey", count=4)
        itemList = InventoryUtil.getAllItemsBelongToUser(guild_id=1, user_id=123)
        assert len(itemList) == 2 and itemList[0].user_id == 123 and itemList[1].user_id == 123

    def test_buyShopitem_failed_noProduct(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10, hidden=True)
        result = InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="he", count=2)
        assert result == ErrorCode.CannotFindProduct
        result == InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hey", count=2)
        assert result == ErrorCode.CannotFindProduct

    def test_buyShopitem_failed_levelDoesNotRequired(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=10)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=100, price=100)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=2)
        assert result == ErrorCode.LevelDoesNotReach

    def test_buyShopitem_failed_noMoney(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=10)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=100)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=2)
        assert result == ErrorCode.TokenDoesNotEnough

    def test_buyShopitem_failed_notEnoughSupply(self):
        MemberUtil.add_member(member_id=123)
        MemberUtil.add_token(member_id=123, amount=100)
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=1)
        result = InventoryUtil.buyShopitem(guild_id=1, user_id=123, item_name="hello", count=2)
        assert result == ErrorCode.SupplyDoesNotEnough

    def test_changeSupplyAmount_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=-1)
        assert shopItem1.amount == -1

        shopItem2 =InventoryUtil.changeSupplyAmount(guild_id=1, item_name="hello", newAmount=10)
        assert shopItem2.amount == 10

    def test_changeSupplyAmount_success_limitedToUnlimited(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        shopItem1 = InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        assert shopItem1.amount == 10

        shopItem2 =InventoryUtil.changeSupplyAmount(guild_id=1, item_name="hello", newAmount=-1)
        assert shopItem2.amount == -1

    def test_changeSupplyAmount_failed(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        # item cannot find
        result1 = InventoryUtil.changeSupplyAmount(guild_id=1, item_name="he", newAmount=-1)
        assert result1 == -1
        # shopitem cannot find
        result2 =InventoryUtil.changeSupplyAmount(guild_id=1, item_name="hey", newAmount=-1)
        assert result2 == -2

    def test_changeShopitemHiddenStatus_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="hello", hidden=True)
        assert result.hidden == True
        result2 = InventoryUtil.ShopMenu(guild_id=1)
        assert len(result2) == 0
        result3 = InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="hello", hidden=False)
        assert result3.hidden == False

    def test_changeShopitemHiddenStatus_failed_noitem(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="he", hidden=True)
        assert result == -1

    def test_changeShopitemHiddenStatus_failed_noShopitem(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="hey", hidden=True)
        assert result == -2

    def test_checkShopitemStatus_success(self):
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        result = InventoryUtil.checkShopitemStatus(guild_id=1, item_name="hello")
        assert result.hidden == False

    def test_checkShopitemStatus_failed(self):
        # no item
        result1 = InventoryUtil.checkShopitemStatus(guild_id=1, item_name="hello")
        assert result1 == -1
        # no shopitem
        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=10)
        result2 = InventoryUtil.checkShopitemStatus(guild_id=1, item_name="hello")
        assert result2 == -2

    def test_listHiddenitem_success(self):
        result = InventoryUtil.listHiddenShopItem(guild_id=1)
        assert len(result) == 0

        ItemUtil.createItem(guild_id=1, item_name="hello", item_type=ItemType.ATTACK, buff_type=BuffType.ATTACK, buff_value=-1, buff_round=2, level_required=0, price=1)
        ItemUtil.createItem(guild_id=1, item_name="hey", item_type=ItemType.STATUS, buff_type=BuffType.DEFENCE, buff_value=10, buff_round=3, level_required=0, price=1)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hello", amount=10)
        InventoryUtil.addItemToShop(guild_id=1, item_name="hey", amount=10)
        InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="hello", hidden=True)
        result = InventoryUtil.listHiddenShopItem(guild_id=1)
        assert len(result) == 1

        # items
        InventoryUtil.changeShopitemHiddenStatus(guild_id=1, item_name="hey", hidden=True)
        result = InventoryUtil.listHiddenShopItem(guild_id=1)
        assert len(result) == 2
