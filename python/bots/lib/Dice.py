from random import randint

def dice(roll_base:int):
    return randint(1, roll_base)
def multi_dice(roll_times:int, roll_base:int):
    return list(str(dice(roll_base)) for r in range(roll_times))
def coc_dice(ref:int, bonus:int):
    result = randint(1,100)
    content = ''
    result_bouns = []
    for b_result in range(abs(bonus)):
        result_bouns.append(dice(10))
    result_bouns.append(int(result/10))
    if min(result_bouns) < int(result/10) and bonus>0:
        result = result%10 + min(result_bouns)*10
    elif max(result_bouns) > int(result/10) and bonus<0:
        result = result%10 + max(result_bouns)*10
    if result <= 1:
        content = '大大大大成功，鱉說話，感受'
    if result <= 5 and ref < 50:
        content = '大失敗拉，50以下是5喔'
    elif result <= int(ref/5):
        content = '極限成功'
    elif result > int(ref/5) and result <= int(ref/2):
        content = '困難成功'
    elif result > int(ref/2) and result <= int(ref):
        content = '普通成功'
    elif result >ref:
        if ref <50 and result > 95:
            content = '大失敗拉，50以下是96喔'
        elif ref >= 50 and result >99:
            content = '大大大大失敗，百分之一歐氣十足'
        else:
            content = '失敗'
    return (str(result), content, str(result_bouns))


if __name__ == '__main__':
    #test fuction
    print("test dice() input 6 resullt =",type(dice(6)),dice(6),)
    print("test multi_dice() input 3,6 resullt =",type(multi_dice(3,6)),multi_dice(3,6))