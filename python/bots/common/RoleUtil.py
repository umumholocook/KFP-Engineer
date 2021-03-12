from common.models.KfpRole import KfpRole

class RoleUtil():

    def updateRole(guild_id: int, role_id: int, role_name: str, color: str):
        query = KfpRole.select().where(guild_id==guild_id, role_id==role_id)
        role: KfpRole
        if query.exists():
            role = query.get()
        else:
            role = KfpRole.create(KfpRole.guild_id==guild_id, role_id==role_id)
        role.role_name = role_name
        role.color = color
        role.save()
        return role

    def updateKfpRoleLevel(role: KfpRole, level: int):
        role.level = level
        role.save()
        return role