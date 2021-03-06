from common.models.Member import Member
from common.KfpDbUtil import KfpDbUtil
import os
from common.KFP_DB import KfpDb

class TestKfpDbUtil():
    def setup_method(self, method):
        self.database = KfpDb(dbFile=":memory:")
        self.testDbPath = os.sep.join((os.getcwd(), "tests", "Database", "KFP_bot_old.db"))
        self.testGuildId = 786612294762889247
        
    def teardown_method(self, method):
        self.database.teardown()

    def test_getCount(self):
        count = KfpDbUtil.getCount(self.testGuildId, self.testDbPath)
        assert count == 11

    def test_utilImport(self):
        insertedDataCount = KfpDbUtil.importFromOldDatabase(self.testGuildId, self.testDbPath)
        count = KfpDbUtil.getCount(self.testGuildId, self.testDbPath)
        assert count == insertedDataCount