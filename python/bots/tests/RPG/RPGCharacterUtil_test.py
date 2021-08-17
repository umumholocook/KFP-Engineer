from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.KFP_DB import KfpDb

class TestRPGCharacterUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
        
    def teardown_method(self, method):
        self.database.teardown()

    def test_hasAdvantureStarted_noMember(self):
        assert not RPGCharacterUtil.hasAdvantureStared(100)
    
    def test_hasAdvantureStarted_hasMember_notStarted(self):
        self.database.add_member(20)
        assert not RPGCharacterUtil.hasAdvantureStared(20)

    def test_hasAdvantureStarted_started(self):
        member = self.database.add_member(33)
        RPGCharacterUtil.createNewRPGCharacter(member)
        assert RPGCharacterUtil.hasAdvantureStared(33)

    def test_createNewCharacter_success(self):
        member = self.database.add_member(33)
        character = RPGCharacterUtil.createNewRPGCharacter(member)
        assert character.character == member

    def test_createExistedCharacter_false(self):
        member = self.database.add_member(33)
        RPGCharacterUtil.createNewRPGCharacter(member)
        character = RPGCharacterUtil.createNewRPGCharacter(member)
        assert character == None
    
    def test_retireCharacter_notExist(self):
        assert not RPGCharacterUtil.retireRPGCharacter(123)
    
    def test_retireCharacter_notAdventurer(self):
        member = self.database.add_member(33)
        assert not RPGCharacterUtil.retireRPGCharacter(member.member_id)
    
    def test_retireCharacter_success(self):
        member = self.database.add_member(33)
        RPGCharacterUtil.createNewRPGCharacter(member)
        RPGCharacterUtil.retireRPGCharacter(member.member_id)
        assert not RPGCharacterUtil.hasAdvantureStared(member.member_id)

    def test_getRPGChracter_success(self):
        member = self.database.add_member(100)
        rpg = RPGCharacterUtil.createNewRPGCharacter(member)
        rpg_get = RPGCharacterUtil.getRPGCharacter(member)
        assert rpg_get == rpg
    
    def test_getRPGCharacter_successWithId(self):
        member = self.database.add_member(100)
        rpg = RPGCharacterUtil.createNewRPGCharacter(member)
        rpg_get = RPGCharacterUtil.getRPGCharacter(member.member_id)
        assert rpg_get == rpg

    def test_levelUpCharacter_success(self):
        member = self.database.add_member(100)
        rpg: RPGCharacterUtil = RPGCharacterUtil.createNewRPGCharacter(member)
        old_hp = rpg.hp_max 
        old_mp = rpg.mp_max
        old_atk = rpg.attack_basic
        old_def = rpg.defense_basic
        RPGCharacterUtil.levelUpCharacter(member.member_id, 1, 10)
        rpg: RPGCharacterUtil = RPGCharacterUtil.getRPGCharacter(member.member_id)

        assert rpg.hp_max > old_hp
        assert rpg.mp_max > old_mp
        assert rpg.attack_basic > old_atk
        assert rpg.defense_basic > old_def
        