import datetime
import math


def g_time(chapter, how_many_times_one_chapter):
    plan = {}
    start_time = datetime.datetime.strptime('2022-06-07', '%Y-%m-%d')
    start_plan = 0
    weeks = (chapter * how_many_times_one_chapter) // 7
    for i in range(weeks):
        start_time += datetime.timedelta(days=7)
        start_plan += 7 / how_many_times_one_chapter
        if start_plan > chapter:
            start_plan = chapter
        plan[start_time.strftime('%Y-%m-%d')] = start_plan

    return plan


def day_after(today, days):
    return (datetime.datetime.strptime(today, '%Y-%m-%d') + datetime.timedelta(days=days)).strftime('%Y-%m-%d')


def generate_read_book_plan(chapter, how_many_times_one_chapter, start_date, rest_days, path):
    title = f'读书计划: {datetime.datetime.now().strftime("%Y-%m-%d")}\n'
    body = f'开始日期: {start_date}\n'
    end_date = day_after(start_date, chapter * how_many_times_one_chapter + rest_days)
    plan = g_time(chapter, how_many_times_one_chapter)
    with open(path + f'/{datetime.datetime.now().strftime("%Y-%m-%d")}_plan.txt', 'w') as fp:
        fp.write(title)
        fp.write(body)
        for key, value in plan.items():
            fp.write(key + ' 之前: ')
            fp.write(f'共阅读 {value} 章\n')
        date_list = []
        for date in plan.keys():
            date_list.append(date)
        fp.write(f'按照计划，共可以休息: {(datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.datetime.strptime(date_list[-1], "%Y-%m-%d")).days} 天\n')


generate_read_book_plan(
    chapter=29,
    how_many_times_one_chapter=7,
    start_date='2022-06-07',
    rest_days=0,
    path='E:\Files\python_project\work\Script4JJ'
)

