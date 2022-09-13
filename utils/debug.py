# -*- coding: utf-8 -*-
"""

@title:	debug-helper
@author: iDeal0103
@status:	Active
@type:	Process
@created:	9-Spt-2022
@post-History:	9-Spt-2022

comment：
    1. 比较卫星坐标计算情况

"""

# import
import utils.PictureResults as PictureResults
import datetime
import utils.TimeSystem as TimeSystem


# 比较rtklib和本地程序卫星计算结果
def parse_time(timestr1, timestr2):
    """
    timestr1 : year-day-month  year/day/month
    timestr2 : hour:minute:second
    """
    if "/" in timestr1:
        year, month, day = list(map(int, timestr1.split("/")))
    elif "-" in timestr1:
        year, month, day = list(map(int, timestr1.split("-")))
    else:
        print("asdasdsdasas!!!!!")
    hour, minute, second = list(map(float, timestr2.split(":")))
    microsecond = int(1000000 * (second-int(second)))
    second=int(second)
    # print(timestr1, year, month, day)
    the_time = datetime.datetime(year, month, day, int(hour), int(minute), second, microsecond)
    return the_time

def get_Tr_from_ts(ts, time_gap=1):
    if time_gap >= 1:
            Tr = datetime.datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second) + datetime.timedelta(seconds=1)

    else:
        microsecond = ts.microsecond
        print("时间间隔过小")
    return Tr

class orbit_record():
    def __init__(self, svn, x, y, z, dts=''):
        self.svn =svn
        self.x = x
        self.y = y
        self.z = z
        self.dts = dts

    def set_t(self, ts):
        self.ts = ts
        self.Tr = get_Tr_from_ts(ts)


def compare_satobit(pos_trace_file, local_trace_file):
    # 处理pos_trace_file
    pos_trace_orbit_records = []
    pos_trace_data = open(pos_trace_file, "r")
    linedata = pos_trace_data.readline()
    while linedata:
        if " rs=" in linedata:
            timestr1 = linedata[2:12]
            timestr2 = linedata[13:29]
            svn = linedata[33:36]
            x = float(linedata[50:71])
            y = float(linedata[71:92])
            z = float(linedata[92:113])
            dts = float(linedata[117:130])
            pos_trace_orbit_record = orbit_record(svn, x, y, z, dts)
            pos_trace_orbit_record.set_t(parse_time(timestr1, timestr2))
            pos_trace_orbit_records.append(pos_trace_orbit_record)
        linedata = pos_trace_data.readline()
    # 处理local_trace_file
    local_trace_orbit_records = []
    local_trace_data = open(local_trace_file, "r")
    linedata = local_trace_data.readline()
    while linedata:
        if " rs=" in linedata:
            timestr1 = linedata[:10]
            timestr2 = linedata[11:26]
            svn = linedata[31:34]
            x = float(linedata[38:59])
            y = float(linedata[59:80])
            z = float(linedata[80:101])
            # dts = linedata[]
            local_trace_orbit_record = orbit_record(svn, x, y, z, dts)
            local_trace_orbit_record.set_t(parse_time(timestr1, timestr2))
            local_trace_orbit_records.append(local_trace_orbit_record)
        linedata = local_trace_data.readline()
    # 进行记录整理
    x_record_manager = PictureResults.plot_records_manager("orbit-x / m")
    y_record_manager = PictureResults.plot_records_manager("orbit-y / m")
    z_record_manager = PictureResults.plot_records_manager("orbit-z / m")
    dts_record_manager = PictureResults.plot_records_manager("orbit-dts / us")
    ts_record_manager = PictureResults.plot_records_manager("delta ts / s")
    for pos_record in pos_trace_orbit_records:
        local_record = list(filter(lambda o: o.svn == pos_record.svn and o.Tr == pos_record.Tr, local_trace_orbit_records))
        if local_record:
           local_record = local_record[0]
           x_record_manager.add_plot_record(PictureResults.plot_record(local_record.Tr, local_record.x-pos_record.x, local_record.svn))
           y_record_manager.add_plot_record(PictureResults.plot_record(local_record.Tr, local_record.y - pos_record.y, local_record.svn))
           z_record_manager.add_plot_record(PictureResults.plot_record(local_record.Tr, local_record.z - pos_record.z, local_record.svn))
           ts_record_manager.add_plot_record(PictureResults.plot_record(local_record.Tr, TimeSystem.cal_deltatime_second(local_record.ts - pos_record.ts), local_record.svn))
        else:
            print(str(pos_record.Tr), " ", pos_record.svn, "未找到对应记录")
    x_record_manager.plot_all_records()
    y_record_manager.plot_all_records()
    z_record_manager.plot_all_records()
    ts_record_manager.plot_all_records()
    # ts_record_manager.plot_by_labels(['C20', 'C23'])

if __name__ == "__main__":
    # pos_trace_file = r"D:\Desktop\暑假冲刺\WARN_BDSsingle_rtklib.pos.trace"
    # local_trace_file = r"D:\Desktop\pnt2_bds.txt"
    # pos_trace_file = r"D:\Desktop\暑假冲刺\WARN_GPSsingle_rtklib.pos.trace"
    # local_trace_file = r"D:\Desktop\pnt2_gps.txt"

    # pos_trace_file = "D:\Desktop\暑假冲刺\zimm3100_wba2_rtk.pos.trace"
    # local_trace_file = "D:\Desktop\wab2_baseline.txt"
    pos_trace_file = "D:\Desktop\暑假冲刺\zimm3100_zim2_rtk.pos.trace"
    local_trace_file = "D:\Desktop\wab2_baseline.txt"
    compare_satobit(pos_trace_file, local_trace_file)



