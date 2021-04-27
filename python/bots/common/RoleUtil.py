from common.KFP_DB import KfpDb
from common.models.KfpRole import KfpRole
from common.Util import Util

class RoleUtil():

    def getRole(guild_id: int, role_id: int):
        query = KfpRole.select().where(KfpRole.guild_id==guild_id, KfpRole.role_id==role_id)
        if query.exists():
            return query.get()
        return None
    
    def getKfpRolesBeforeLevel(guild_id: int, level: int):
        query = KfpRole.select().where(KfpRole.guild_id == guild_id, level > KfpRole.level)
        result = []
        if query.exists():
            for role in query.order_by(KfpRole.level.desc()).iterator():
                result.append(role)
        return result

    def getKfpRolesFromLevel(guild_id: int, level: int):
        query = KfpRole.select().where(KfpRole.guild_id == guild_id, level >= KfpRole.level)
        roles = {}
        if query.exists():
            for role in query.order_by(KfpRole.level.desc()).iterator():
                if role.category not in roles:
                    roles[role.category] = role
        return list(roles.values())

    def getKfpRoleFromLevel(guild_id: int, level: int):
        query = KfpRole.select().where(KfpRole.guild_id == guild_id, level >= KfpRole.level)
        if query.exists():
            return query.order_by(KfpRole.level.desc()).get()
        return None

    def updateRole(guild_id: int, role_id: int, role_name: str, color: str, category: int = 0):
        query = KfpRole.select().where(KfpRole.guild_id==guild_id, KfpRole.role_id==role_id)
        role: KfpRole
        if query.exists():
            role = query.get()
        else:
            role = KfpRole.create(guild_id = guild_id, role_id = role_id, role_name = role_name, color = color, category = category)
        role.role_name = role_name
        role.color = color
        role.save()
        return role

    def updateKfpRoleLevel(role: KfpRole, level: int):
        role.level = level
        role.save()
        return role

    def getCurrentRoles(guild_id: int, category: Util.RoleCategory = None):
        if category:
            query = KfpRole.select().where(KfpRole.guild_id == guild_id, KfpRole.category == category)
        else:
            query = KfpRole.select().where(KfpRole.guild_id == guild_id)
        result = []
        if query.exists():
            for role in query.iterator():
                result.append(role)
        return result

    def deleteAllData():
        KfpRole.drop_table()

    def wipeDataAndKeepTable():
        KfpRole.drop_table()
        KfpRole.create_table()

