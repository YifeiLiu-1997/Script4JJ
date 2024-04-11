"""
@Project     :Script4JJ 
@File        :old_shit.py
@IDE         :PyCharm 
@Author      :LYF
@Date        :2024/3/28 11:15
@Description :养老金=基础养老金+个人账户养老金
个人账户养老金=个人账户储存额÷计发月数(50岁为195、55岁为170、60岁为139,不再统一是120了)
基础养老金=(全省上年度在岗职工月平均工资+本人指数化月平均缴费工资)÷2×缴费年限×1% =全省上年度在岗职工月平均工资(1+本人平均缴费指数)÷2×缴费年限×1%
"""


def cal_old_shit(current_base, gender, age, increase, current_old, pay_time):
    """以2023退休为例，北京平均 7000"""
    if age > 60:
        return '不能这么算'

    if gender == 'male':
        retire_age = 60
        month = 139
    if gender == 'female':
        retire_age = 50
        month = 195

    # 基础养老金，本人平均缴费指数为 1
    base_old = get_beijing_avg(7000, pay_time) * 2 * pay_time * 0.01
    print(f'基础养老金: {base_old}')

    # 个人账户养老金
    self_old = (current_old + get_self_old(current_old, current_base, increase, retire_age - age)) / month
    print(f'养老金每月: {base_old + self_old}')

    change_old = get_change_old(base_old + self_old, retire_age - age)
    print(f'预算物价上涨后，相当于今年的 {change_old}')
    return base_old + self_old


def get_self_old(current_old, current_base, increase, pay_time):
    old_count = 0
    for i in range(pay_time):
        old_shit = current_base * (0.08 + 0.16) * 12
        old_count += old_shit
        current_base += current_base * increase

    print(f'到退休养老金账户余额: {current_old + old_count}')
    print(f'最后工资基数: {current_base}')
    return old_count


def get_beijing_avg(now, pay_time):
    for i in range(pay_time):
        now += now * 0.01
    return now


def get_change_old(month_old, pay_time):
    stack = 1
    for i in range(pay_time):
        stack += stack * 0.01

    return month_old / stack


if __name__ == '__main__':
    cal_old_shit(
        current_base=11000,
        gender='male',
        increase=0.01,
        age=26,
        current_old=0,
        pay_time=34,
    )
