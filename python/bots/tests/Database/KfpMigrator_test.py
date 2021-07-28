from common.models.Member import Member
from common.database.KfpMigrator import KfpMigrator
import os, shutil
from common.KFP_DB import KfpDb

class TestKfpMigrator():
    def setup_method(self, method):
        pass
        
    def teardown_method(self, method):
        pass
    
    def test_memberTokenMigration(self):
        oldDbPath = getDBPath("old.db")
        testDbPath = getDBPath("test.db")
        shutil.copyfile(oldDbPath, testDbPath)

        database = KfpDb(testDbPath)
        assert KfpMigrator.KfpMigrate(database.sqliteDb)
        database.teardown()
        os.remove(testDbPath)
    
    # def test_itemDropHiddenMigration(self):
    #     oldDbPath = getDBPath("item_has_hidden.db")
    #     testDbPath = getDBPath("test.db")
    #     shutil.copyfile(oldDbPath, testDbPath)
    #
    #     database = KfpDb(testDbPath)
    #     assert KfpMigrator.KfpMigrate(database.sqliteDb)
    #     database.teardown()
    #     os.remove(testDbPath)

    def test_withRegularDatabase(self):
        database = KfpDb(":memory:")
        
        database.add_member(1)
        member: Member = database.get_member(1)
        assert member

def getDBPath(dbName: str):
    return os.sep.join((os.getcwd(), "tests", "Database", dbName))