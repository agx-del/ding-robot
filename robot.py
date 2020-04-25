
#! /usr/bin/env python
# coding: utf-8

import requests
import json
import time
import datetime
import math

IF_SKIP_IMD_SEND = True  # True  # 发布时要改
START_SEND_HOUR = 8
TIME_DIFF = 12  #12 # 发布时要改
FIRST_SHIFT_WEEK = 1
FIRST_CLEAN_WEEK = 2
CLEAN_WEEKDAY = 5
# 测试群：
#ROBOT_TOKEN = "https://oapi.dingtalk.com/robot/send?access_token=096f7af3a2df5c960da438f19cabe6063b208dfb81a1e846a97edafce27be012"

# 正式群
ROBOT_TOKEN = "https://oapi.dingtalk.com/robot/send?access_token=b302087ce3f6327b37abbd49c5cae63af87119bc48aa247d12e1043c78d33cd4"


class ShiftSch:
    def __init__(self, day):
        self.clean_weekday = CLEAN_WEEKDAY
        self.day = day

        self.school_day = SchoolDay(self.day)
        self.wutuo_candidates = Candidates(15)
        self.zhiyue_candidates = Candidates()

        self.wutuo_candidates.add_people("方彦童", day_seq=1)
        self.wutuo_candidates.add_people("张熙玥", day_seq=2)
        self.wutuo_candidates.add_people("林一淳", day_seq=3)
        self.wutuo_candidates.add_people("欧阳文俊", day_seq=4)
        self.wutuo_candidates.add_people("于嘉晔", day_seq=5)
        self.wutuo_candidates.add_people("林睿哲", day_seq=6)
        self.wutuo_candidates.add_people("周璟晖", day_seq=7)
        self.wutuo_candidates.add_people("李泽锋", day_seq=8)
        self.wutuo_candidates.add_people("康永鑫", day_seq=9)
        self.wutuo_candidates.add_people("简子雄", day_seq=10)
        self.wutuo_candidates.add_people("谢伽怡", day_seq=11)
        self.wutuo_candidates.add_people("郭友为", day_seq=12)
        self.wutuo_candidates.add_people("麻语祺", day_seq=13)
        self.wutuo_candidates.add_people("王昱懿", day_seq=14)
        self.wutuo_candidates.add_people("陈信安", day_seq=15)

        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,2,19).date(),["张熙玥","test"])
        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,4,8).date(),["于嘉晔"])
        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,4,29).date(),["李泽锋"])
        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,5,20).date(),["张熙玥"])
        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,6,10).date(),["张浩轩"])
        self.wutuo_candidates.add_extra_duty(datetime.datetime(2019,7,1).date(),["陈信安"])

        self.zhiyue_candidates.add_extra_duty(datetime.datetime(2019,3,15).date(),["张浩轩","陈信安"])
        self.zhiyue_candidates.add_extra_duty(datetime.datetime(2019,4,12).date(),["张熙玥","郭友为"])
        self.zhiyue_candidates.add_extra_duty(datetime.datetime(2019,5,17).date(),["林睿哲","方彦童"])
        self.zhiyue_candidates.add_extra_duty(datetime.datetime(2019,6,14).date(),["李昭逸","徐婧"])
        self.zhiyue_candidates.add_extra_duty(datetime.datetime(2019,7,12).date(),["康永鑫","周璟晖"])

    def set_day(self, day):
        self.day = day
        self.school_day.set_day(day)

    def _get_wutuo_people(self):
        shift_people = []
        shift_names = ""
        if self.school_day.is_school_day():
            return ""
        spec_date_seq = self.school_day.get_date_seq()
        for candidate in self.wutuo_candidates.peoples:
            if (spec_date_seq-1) % self.wutuo_candidates.round + 1 == candidate.day_seq:
                shift_people.append(candidate)
                shift_names += (candidate.name+"")
        return shift_people

    def get_wutuo_people_names(self):
        shift_people = self._get_wutuo_people()
        ret = ""
        if len(shift_people) > 0:
            ret = ", ".join([(p.name) for p in shift_people])
        if self.wutuo_candidates.is_extra_duty_date(self.day): #若为特别指定的值日人员，则以此为准
            extra_duty_names = self.wutuo_candidates.get_extra_duty_candidate_name(self.day)
            ret =  ", ".join(extra_duty_names)
        if ret != "":
            return "**"+ret+"**"
        else:
            return ""

    def get_zhiyue_people_names(self):
        ret = ""
        if self.zhiyue_candidates.is_extra_duty_date(self.day): #若为特别指定的值日人员，则以此为准
            extra_duty_names = self.zhiyue_candidates.get_extra_duty_candidate_name(self.day)
            ret =  ", ".join(extra_duty_names)
        if ret != "":
            return "**"+ret+"**"
        else:
            return ""


class SchoolDay:
    def __init__(self, day):
        self.first_day = datetime.datetime(2019, 2, 18, 0, 0, 0, 1)
        self.first_shift_week = FIRST_SHIFT_WEEK
        self.first_clean_week = FIRST_CLEAN_WEEK
        self.clean_weekday = CLEAN_WEEKDAY
        self.day = day

        self.skip_days = []
        self.skip_days_with_desc = []

        self.add_skip_day(
            datetime.datetime(2019, 4, 5, 0, 0, 1), "清明假期")
        self.add_skip_day(
            datetime.datetime(2019, 5, 1, 0, 0, 1), "五一假期")
        self.add_skip_day(
            datetime.datetime(2019, 5, 2, 0, 0, 1), "五一假期")
        self.add_skip_day(
            datetime.datetime(2019, 5, 3, 0, 0, 1), "五一假期")
        self.add_skip_day(
            datetime.datetime(2019, 10, 1, 0, 0, 1), "国庆假期")

    def set_day(self, day):
        self.day = day

    def _get_spec_week(self, spec_day):
        diff_days = spec_day - self.first_day
        return math.floor(diff_days.days/7)+1

    def get_week(self):
        return self._get_spec_week(self.day)

    def get_term_week_seq(self):
        if self._get_spec_week(self.day) - self._get_spec_week(self.first_day) < 0:
            return -1  # 如果查询的日期在开学前，则返回-1
        else:
            return self._get_spec_week(self.day) - self._get_spec_week(self.first_day)+1

    def is_weekend(self):
        return self.day.isocalendar()[2] > 5

    def is_school_day(self):  # 是否为正常上学日期（不含跳过日期）
        is_skip_day = self.day.isocalendar() in self.skip_days
        return (is_skip_day or self.is_weekend())

    def get_skip_day_desc(self, day):
        spec_day = day if day != "" else self.day
        for skip_day in self.skip_days_with_desc:
            if spec_day.isocalendar() == skip_day.day:
                return skip_day.desc+", "
        return ""

    def get_date_seq(self):
        return (self.get_term_week_seq()-1)*5 + self.day.weekday()+1
        # return (self.day - self.first_day).days+1 - (self._get_spec_week(self.day)-1)*2

    def add_skip_day(self, skip_day, desc=""):
        try:
            if skip_day.isocalendar() not in self.skip_days:  # 添加跳过的日期
                self.skip_days.append(skip_day.isocalendar())
                self.skip_days_with_desc.append(
                    SpecialDay(skip_day.isocalendar(), desc))
        except:
            print("[ERROR] SchoolDay:add_skip_clean_week input error!")

    def get_weekday_date_desc(self, day=""):
        spec_day = day if day != "" else self.day
        return "周"+"一二三四五六日"[spec_day.weekday()]+"("+str(spec_day.strftime("%m/%d"))+")"

    def get_day_desc(self, day=""):
        spec_day = day if day != "" else self.day
        return self.get_skip_day_desc(spec_day)


class People:
    def __init__(self, name, week_flg=-1, week_day=-1, day_seq=-1, week_seq=-1):
        self.name = name
        self.week_flg = week_flg
        self.week_day = week_day
        self.day_seq = day_seq
        self.week_seq = week_seq


class Candidates:
    def __init__(self, round=-1):
        self.peoples = []
        self.extra_duty = []
        self.round = round

    def add_people(self, name, week_flg=-1, week_day=-1, day_seq=-1, week_seq=-1):
        p = People(name, week_flg, week_day, day_seq, week_seq)
        self.peoples.append(p)

    def add_extra_duty(self, spec_date, people_name=[]):
        self.extra_duty.append(DaySch(spec_date, people_name))

    def is_extra_duty_date(self, spec_date):
        for extra_duty_sch in self.extra_duty:
            if spec_date.date() == extra_duty_sch.date:
                return True
        return False

    def get_extra_duty_candidate_name(self, spec_date):
        for extra_duty_sch in self.extra_duty:
            if spec_date.date() == extra_duty_sch.date:
                return extra_duty_sch.people_name
        return ""

class DaySch:
    def __init__(self, spec_date, people_name=[]):
        self.date = spec_date
        self.people_name = people_name


class SpecialDay:
    def __init__(self, day, desc=""):
        self.day = day
        self.desc = desc


class TodayDesc:
    def __init__(self, today):
        self.today = today
        self.shift_sch = ShiftSch(self.today)
        self.school_day = SchoolDay(self.today)
        self.str_prefix = "- "

    def get_desc(self):
        if self.today.isocalendar()[2] > 5:  # 若为周末则显示下周值日情况
            str_content = "新的一周安排：\n\n"+self.get_next_days_desc()
        else:
            str_content = self.get_today_desc() + self.get_tomorrow_desc()

        ret = self.get_prefix() +\
            str_content +\
            self.get_suffix()
        return ret

    def get_prefix(self):
        self.shift_sch.set_day(self.today)
        self.school_day.set_day(self.today)
        ret = "今天是" + str(self.today.strftime("%m/%d")) +\
            "，周" + \
            "一二三四五六日"[self.today.weekday()]
        ret = ret+"(第" + str(self.school_day.get_week()) + \
            "周)：\n\n" if self.today.weekday() < 5 else ret + "\n\n"
        return ret

    def get_suffix(self):
        ret = "\n\n谢谢！" +\
            "\n\n　\n\n> 机器人不会回答，请不要@他"
        return ret

    def _get_wutuo_desc(self, day, desc_prefix=""):
        prefix = self.str_prefix+desc_prefix
        self.shift_sch.set_day(day)
        self.school_day.set_day(day)
        wutuo_candidates_names = self.shift_sch.get_wutuo_people_names()
        if wutuo_candidates_names != "":
            wutuo_str = "请 " + \
                str(wutuo_candidates_names)+" 的家长午托值日\n\n"
            return prefix+wutuo_str
        else:
            return prefix+self.school_day.get_day_desc()+"无需安排家长午托值日。\n\n"

    def get_today_desc(self):
        ret =  self._get_wutuo_desc(self.today, "今天")
        zhiyue_str = self._get_zhiyue_desc(self.today, "今天")
        if zhiyue_str != "":
            ret = ret + zhiyue_str
        return ret

    def get_tomorrow_desc(self):
        ret =  self._get_wutuo_desc(self.today+datetime.timedelta(days=1), "明天")
        zhiyue_str = self._get_zhiyue_desc(self.today+datetime.timedelta(days=1), "明天")
        if zhiyue_str != "":
            ret = ret + zhiyue_str
        return ret

    def _get_zhiyue_desc(self, day, desc_prefix=""):
        prefix = self.str_prefix+desc_prefix
        self.shift_sch.set_day(day)
        self.school_day.set_day(day)
        zhiyue_candidates_names = self.shift_sch.get_zhiyue_people_names()
        if zhiyue_candidates_names != "":
            wutuo_str = "请 " + \
                str(zhiyue_candidates_names)+" 的家长放学后来教室做窗子及室内的月度清洁\n\n"
            return prefix+wutuo_str
        else:
            return ""

    def get_next_days_desc(self, day_cnt=5):
        ret = ""
        for i in range(day_cnt):
            cur_day = self.today + \
                datetime.timedelta(days=(7-self.today.weekday()+i))
            ret = ret + \
                self._get_wutuo_desc(
                    cur_day, self.school_day.get_weekday_date_desc(cur_day)+", ")
            zhiyue_str = self._get_zhiyue_desc(cur_day, self.school_day.get_weekday_date_desc(cur_day)+", ")
            if zhiyue_str != "":
                ret = ret + zhiyue_str
        return ret


def main():
    today = datetime.datetime.now()+datetime.timedelta(hours=TIME_DIFF)

    if IF_SKIP_IMD_SEND:
        today_day = today.day
        is_finished_today = True
    else:
        today_day = -1
        is_finished_today = False

    while(True):
        today = datetime.datetime.now()+datetime.timedelta(hours=TIME_DIFF)

        if today_day != today.day:
            today_day = today.day
            out_str = TodayDesc(today).get_desc()
            if out_str != "":
                # 今日需发布信息
                is_finished_today = False
            else:
                is_finished_today = True
        else:
            # 当天未过完
            #print("date match.")
            pass
        if today.hour >= START_SEND_HOUR and is_finished_today == False:  # 满足发消息条件，开始组装字符串
            is_finished_today = True
            if out_str != "":
                dingding_url = ROBOT_TOKEN
                headers = {
                    "Content-Type": "application/json; charset=utf-8"}
                post_data = {
                    "msgtype": "markdown",
                    "markdown": {
                        # "content": out_str
                        "title": "家长义工安排...",
                        "text": out_str
                    },
                    # "at": {
                    # "isAtAll": True
                    # "atMobiles": [
                    #    "13760200000",
                    #    "13760200001"
                    # ]
                    # }
                }

                print("\n\n\nout str is:\n\n%s" % out_str)
                # print("out is:%s" % post_data)
                r = requests.post(dingding_url, headers=headers,
                                  data=json.dumps(post_data))
                # print(r.content)
            # else:
            #    print("time not match or already finished today, waiting...")
        time.sleep(60)


if __name__ == "__main__":

    main()
