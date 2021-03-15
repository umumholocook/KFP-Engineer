
from common.Util import Util
from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
from common.KFP_DB import KfpDb

class TestRoleUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
        pass
    def teardown_method(self, method):
        self.database.teardown()
        pass

    def test_updateRoleCreateNewOne(self):
        role: KfpRole = RoleUtil.updateRole(123, 321, "testing", "0x000345")
        
        assert role.guild_id == 123
        assert role.role_id == 321
        assert role.role_name == "testing"
        assert role.color == "0x000345"

    def test_updateRoleUpdateOldOne(self):
        RoleUtil.updateRole(123, 321, "testing", "0x000345")
        role: KfpRole = RoleUtil.updateRole(123, 321, "onetwothree", "0x000543")

        assert role.role_name == "onetwothree"
        assert role.color == "0x000543"

    def test_updateKfpRoleLevelZero(self):
        RoleUtil.updateRole(123, 321, "testing", "0x000345")
        role: KfpRole = RoleUtil.getRole(123, 321)

        assert role.level == 0

    def test_updateKfpRoleLevelSuccess(self):
        RoleUtil.updateRole(123, 321, "testing", "0x000345")
        role: KfpRole = RoleUtil.getRole(123, 321)
        RoleUtil.updateKfpRoleLevel(role, 20)

        assert role.level == 20

    def test_getCurrentRolesEmpty(self):
        roleList = RoleUtil.getCurrentRoles(123)
        assert len(roleList) == 0

    
    def test_getCurrentRolesSuccess(self):
        role1 = RoleUtil.updateRole(123, 321, "testing", "0x000345")
        role2 = RoleUtil.updateRole(123, 123, "onetwothree", "0x000543")
        roleList = RoleUtil.getCurrentRoles(123)
        assert len(roleList) == 2
        assert roleList[0] == role1
        assert roleList[1] == role2

    def test_getRoleFromLevel(self):
        role1 = RoleUtil.updateRole(123, 321, "testing", "0x000345")
        RoleUtil.updateKfpRoleLevel(role1, 10)
        role2 = RoleUtil.updateRole(123, 123, "onetwothree", "0x000543")
        RoleUtil.updateKfpRoleLevel(role2, 20)

        role = RoleUtil.getKfpRoleFromLevel(123, 9)
        assert not role
        role = RoleUtil.getKfpRoleFromLevel(123, 11)
        assert role == role1 
        role = RoleUtil.getKfpRoleFromLevel(123, 20)
        assert role == role2 