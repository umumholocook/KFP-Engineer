import math
from common.models.Member import Member
from peewee import *

class MemberUtil():
    def get_total_coin():
        query = Member.select(fn.SUM(Member.coin))
        if query.exists():
            return query.scalar()
        return 0
    
    def get_total_token():
        query = Member.select(fn.SUM(Member.token))
        if query.exists():
            return query.scalar()
        return 0

    def get_member_count():
        query = Member.select(fn.Count())
        if query.exists():
            return query.scalar()
        return 0

    def add_member(member_id:int):
        member = Member.create(member_id=member_id)
        member.save()
        return member

    def add_token(member_id: int, amount: int):
        query = Member.select().where(Member.member_id == member_id)
        if query.exists():
            member = query.get()
        else:
            member = MemberUtil.add_member(member_id)
        member.token += amount
        member.save()

    def add_coin(member_id: int, amount: int):
        query = Member.select().where(Member.member_id == member_id)
        if query.exists():
            member = query.get()
        else:
            member = MemberUtil.add_member(member_id)
        member.coin += amount
        member.save()
        
    def subtract_coin(member: Member, amount: int):
        if member == None: return
        member.coin -= abs(amount)
        member.save()
        
    def add_token_to_member(member: Member, amount: int):
        if member == None: return
        member.token += amount
        member.save()

    def get_member(member_id:int):
        query = Member.select().where(Member.member_id == member_id)
        if query.exists():
            return query.get()
        return None
    
    def get_or_add_member(member_id:int):
        query = Member.select().where(Member.member_id == member_id)
        if query.exists():
            return query.get()
        return MemberUtil.add_member(member_id)
