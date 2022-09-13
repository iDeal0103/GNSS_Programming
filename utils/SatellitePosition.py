# -*- coding: utf-8 -*-
"""

@title:	Style Guide for Python Code
@author: iDeal0103
@status:	Active
@type:	Process
@created:	13-Apr-2021
@post-History:	13-Apr-2021

comment:
    1.计算某时刻某卫星坐标
    2.计算某时刻某卫星钟差

"""

# import
import utils.const as const
import utils.TimeSystem as TimeSystem
import math
import utils.DoFile as DoFile
import datetime
import utils.RecordFilter as RecordFilter
import numpy as np
import utils.ResultAnalyse as ResultAnalyse


# 以某条记录为基础,计算卫星位置
def cal_SatellitePosition_GPS_datetime(time, serial_no, brs):
    """
    Parameters
    ----------
        time : datetime.datetime,所求时刻的datetime格式的GPS时间
        brs : list[GPS_brdc_record class],所依据的广播星历记录
    Returns
    -------
        X,Y,Z ：卫星的三维坐标(单位为m)
    """
    # 筛选出最接近的一条记录
    br = RecordFilter.find_closest_record(brs, time, serial_no)
    # (1)Time from ephemeris epoch toe
    tk = TimeSystem.from_datetime_cal_GPSws(time)[1] - br.toe
    # (2)Calculate the semimajor axis
    a = br.sqrt_a ** 2
    # (3)Compute mean motion – rad/s
    n0 = math.sqrt(const.miu / a ** 3)
    # (4)Correct mean motion
    n = n0 + br.delta_n
    # (5)Mean anomaly Mk at epoch t
    Mk = br.M0 + n * tk
    # (6)Eccentricity anomaly Ek at epoch t
    Ek = cal_Ek(Mk, br.e)
    # (7)True anomaly vk at epoch t
    vk = 2 * math.atan(math.sqrt(1 - br.e ** 2) / (1 - br.e) * math.tan(Ek / 2))
    # (8)argument of latitude
    uk = vk + br.w
    # (9)Corrections for second harmonic perturbations
    delta_uk = br.Cuc * math.cos(2 * uk) + br.Cus * math.sin(2 * uk)
    delta_rk = br.Crc * math.cos(2 * uk) + br.Crs * math.sin(2 * uk)
    delta_ik = br.Cic * math.cos(2 * uk) + br.Cis * math.sin(2 * uk)
    # (10) Corrected argument of latitude, radius and inclination
    u = uk + delta_uk
    r = a * (1 - br.e * math.cos(Ek)) + delta_rk
    i = br.i0 + delta_ik + br.i_dot * tk
    # (11) Satellites’ positions in orbital plane
    x = r * math.cos(u)
    y = r * math.sin(u)
    # (12) Corrected longitude of ascending node at epoch t
    lamb = br.omega0 + (br.omega_dot - const.we) * tk - const.we * br.toe
    # (13) Satellites coordinates at ECEF system
    poscoor_ECEF_X = r * (math.cos(u) * math.cos(lamb) - math.sin(u) * math.cos(i) * math.sin(lamb))
    poscoor_ECEF_Y = r * (math.cos(u) * math.sin(lamb) + math.sin(u) * math.cos(i) * math.cos(lamb))
    poscoor_ECEF_Z = r * math.sin(u) * math.sin(i)
    # 输出坐标单位为m
    return poscoor_ECEF_X, poscoor_ECEF_Y, poscoor_ECEF_Z


# 以某条记录为基础,计算卫星钟差
def cal_ClockError_GPS_datetime(time, serial_no, brs):
    """
    Parameters
    ----------
        time : datetime.datetime,所求时刻的datetime格式的GPS时间
        brs : list[GPS_brdc_record class],所依据的广播星历记录
    Returns
    -------
        clockerror ：卫星的钟差,单位s
    """
    # 筛选出最接近的一条记录
    br = RecordFilter.find_closest_record(brs, time, serial_no)
    print(time, br.toc)
    tc = TimeSystem.from_datetime_cal_GPSws(time)[1] - br.toe
    print(tc, TimeSystem.from_datetime_cal_GPSws(time)[1], br.toe)
    clockerror = br.a0 + br.a1 * tc + br.a2 * tc ** 2
    return clockerror


# 卫星位置计算中求解Ek所用函数
def cal_Ek(Mk, e):
    Ek1 = Mk
    Ek0 = 0.0
    while (abs(Ek1 - Ek0) > 1.0e-12):
        Ek0 = Ek1
        Ek1 = Mk + e * math.sin(Ek0)
    Ek = Ek1
    return Ek


# 以某条记录为基础,计算卫星位置
def cal_SatellitePosition_GPS_GPSws(time, serial_no, brs):
    """
    Parameters
    ----------
        time : GPSws,所求时刻的GPSws类的GPS时间
        brs : list[GPS_brdc_record class],所依据的广播星历记录
    Returns
    -------
        X,Y,Z ：卫星的三维坐标(单位为m)
        dt : 卫星的钟差
    """
    # 筛选出最接近的一条记录
    datetime_time = TimeSystem.from_GPSws_cal_datetime_2(time)
    br = RecordFilter.find_closest_record(brs, datetime_time, serial_no)
    # (1)Time from ephemeris epoch toe
    tk = time.GpsSecond - br.toe
    if abs(tk) > 7200:
        print(serial_no + '卫星位置计算效果可能较差!')
    # 必须考虑到一周的开始或结束的交叉时间
    if tk > 302400:
        tk = tk - 604800
    elif tk < -302400:
        tk = tk + 604800
    # (2)Calculate the semimajor axis
    a = br.sqrt_a ** 2
    # (3)Compute mean motion – rad/s
    n0 = math.sqrt(const.miu_GPS / a ** 3)
    # (4)Correct mean motion
    n = n0 + br.delta_n
    # (5)Mean anomaly Mk at epoch t
    Mk = br.M0 + n * tk
    # (6)Eccentricity anomaly Ek at epoch t
    Ek = cal_Ek(Mk, br.e)
    # (7)True anomaly vk at epoch t
    vk = 2 * math.atan(math.sqrt((1 + br.e) / (1 - br.e)) * math.tan(Ek / 2))
    # (8)argument of latitude
    uk = vk + br.w
    # (9)Corrections for second harmonic perturbations
    delta_uk = br.Cuc * math.cos(2 * uk) + br.Cus * math.sin(2 * uk)
    delta_rk = br.Crc * math.cos(2 * uk) + br.Crs * math.sin(2 * uk)
    delta_ik = br.Cic * math.cos(2 * uk) + br.Cis * math.sin(2 * uk)
    # (10) Corrected argument of latitude, radius and inclination
    u = uk + delta_uk
    r = a * (1 - br.e * math.cos(Ek)) + delta_rk
    i = br.i0 + delta_ik + br.i_dot * tk
    # (11) Satellites’ positions in orbital plane
    x = r * math.cos(u)
    y = r * math.sin(u)
    # (12) Corrected longitude of ascending node at epoch t
    lamb = br.omega0 + (br.omega_dot - const.we_GPS) * tk - const.we_GPS * br.toe
    # (13) Satellites coordinates at ECEF system
    poscoor_ECEF_X = r * (math.cos(u) * math.cos(lamb) - math.sin(u) * math.cos(i) * math.sin(lamb))
    poscoor_ECEF_Y = r * (math.cos(u) * math.sin(lamb) + math.sin(u) * math.cos(i) * math.cos(lamb))
    poscoor_ECEF_Z = r * math.sin(u) * math.sin(i)
    # info = str(datetime_time) + " " + br.SVN + " lamb=%20.6f x=%20.6f y=%20.6f i=%20.6f" % (lamb, x, y, i)
    # ResultAnalyse.trace(info)
    # 坐标单位化为m
    return poscoor_ECEF_X, poscoor_ECEF_Y, poscoor_ECEF_Z


# 以某条记录为基础,计算BDS卫星位置
def cal_SatellitePosition_BDS_GPSws(time, serial_no, brs):
    """
    Parameters
    ----------
        time : GPSws,所求时刻的GPSws类的GPS时间
        brs : list[Renix304_navigation_record_BDS class],所依据的广播星历记录
    Returns
    -------
        X,Y,Z ：卫星在地心地固坐标系下的的三维坐标(单位为m)
    """
    # 筛选出最接近的一条记录
    datetime_time = TimeSystem.from_GPSws_cal_datetime_2(time)
    # BDSws = TimeSystem.from_GPSws_get_BDSws(time)
    BDSws = TimeSystem.BDSws(time.GpsWeek, time.GpsSecond)
    br = RecordFilter.find_closest_record(brs, datetime_time, serial_no)
    # (1)Time from ephemeris epoch toe
    tk = BDSws.BDSSecond - br.toe
    if abs(tk) > 7200:
        print(br.SVN, '效果可能较差!')
    if tk > 302400:
        tk = tk - 604800
    elif tk < -302400:
        tk = tk + 604800
    # (2)Calculate the semimajor axis
    a = br.sqrt_a ** 2
    # (3)Compute mean motion – rad/s
    n0 = math.sqrt(const.miu_BDS / a ** 3)
    # (4)Correct mean motion
    n = n0 + br.delta_n
    # (5)Mean anomaly Mk at epoch t
    Mk = br.M0 + n * tk
    # (6)Eccentricity anomaly Ek at epoch t
    Ek = cal_Ek(Mk, br.e)
    # (7)True anomaly vk at epoch t
    vk = 2 * math.atan(math.sqrt((1 + br.e) / (1 - br.e)) * math.tan(Ek / 2))
    # (8)argument of latitude
    uk = vk + br.w
    # (9)Corrections for second harmonic perturbations
    delta_uk = br.Cuc * math.cos(2 * uk) + br.Cus * math.sin(2 * uk)
    delta_rk = br.Crc * math.cos(2 * uk) + br.Crs * math.sin(2 * uk)
    delta_ik = br.Cic * math.cos(2 * uk) + br.Cis * math.sin(2 * uk)
    # (10) Corrected argument of latitude, radius and inclination
    u = uk + delta_uk
    r = a * (1 - br.e * math.cos(Ek)) + delta_rk
    i = br.i0 + delta_ik + br.i_dot * tk
    # r = a * (1-br.e * math.cos(Ek))
    # (11) Satellites’ positions in orbital plane
    # u = uk
    x = r * math.cos(u)
    y = r * math.sin(u)
    if br.SVN in ["C01", "C02", "C03", "C04", "C05", "C59", "C60"]:  # GEO卫星的计算
        lamb = br.omega0 + br.omega_dot * tk - const.we_BDS * (br.toe-14)
        Xg = x * math.cos(lamb) - y * math.cos(i) * math.sin(lamb)
        Yg = x * math.sin(lamb) + y * math.cos(i) * math.cos(lamb)
        Zg = y * math.sin(i)
        sino = math.sin(const.we_BDS * tk)
        coso = math.cos(const.we_BDS * tk)
        poscoor_ECEF_X = Xg * coso + Yg * sino * math.cos(-5 / 180 * math.pi) + Zg * sino * math.sin(-5 / 180 * math.pi)
        poscoor_ECEF_Y = -Xg * sino + Yg * coso * math.cos(-5 / 180 * math.pi) + Zg*coso * math.sin(-5 / 180 * math.pi)
        poscoor_ECEF_Z = -Yg * math.sin(-5 / 180 * math.pi) + Zg * math.cos(-5 / 180 * math.pi)
    else:
        # (12) Corrected longitude of ascending node at epoch t
        lamb = br.omega0 + (br.omega_dot - const.we_BDS) * tk - const.we_BDS * (br.toe-14)
        # (13) Satellites coordinates at ECEF system
        poscoor_ECEF_X = x * math.cos(lamb) - y * math.cos(i) * math.sin(lamb)
        poscoor_ECEF_Y = x * math.sin(lamb) + y * math.cos(i) * math.cos(lamb)
        poscoor_ECEF_Z = y * math.sin(i)
        # info = str(datetime_time) + " " + br.SVN + " lamb=%20.6f x=%20.6f y=%20.6f i=%20.6f" % (lamb, x, y, i)
        # ResultAnalyse.trace(info)
    return poscoor_ECEF_X, poscoor_ECEF_Y, poscoor_ECEF_Z


# 以某条记录(GPSweek和GPSsecond)为基础,计算卫星钟差
def cal_ClockError_GPSws(time, SVN, brs):
    """
    Parameters
    ----------
        time : GPSws,所求时刻的GPSws类的GPS时间
        SVN : str,卫星的SVN
        brs : list[GPS_brdc_record class],所依据的广播星历记录
    Returns
    -------
        clockerror : 卫星钟差,单位s
    """
    # 筛选出最接近的一条记录
    datetime_time = TimeSystem.from_GPSws_cal_datetime_2(time)
    br = RecordFilter.find_closest_record(brs, datetime_time, SVN)
    tc = time.GpsSecond - br.toe
    clockerror = br.a0 + br.a1 * tc + br.a2 * tc ** 2
    return clockerror


# 以某条记录(GPSweek和GPSsecond)为基础,计算卫星钟差(包含相对论效应)
def cal_ClockError_GPSws_withRelativisticEffect(time, SVN, brs, system="G"):
    """
    Parameters
    ----------
        time : GPSws,所求时刻的GPSws类的GPS时间
        SVN : str,卫星的SVN号
        brs : list[GPS_brdc_record class],所依据的广播星历记录
        system : "G""C""E"等， 卫星系统
    Returns
    -------
        clockerror : 卫星钟差,单位s
    """
    # 获得系统对应的常数
    if system == "G":
        miu = const.miu_GPS
    elif system == "C":
        miu = const.miu_BDS
    # 筛选出最接近的一条记录
    # 由GPSws类数据得到datetime.datetime类型时间,便于筛选数据
    datetime_time = TimeSystem.from_GPSws_cal_datetime_2(time)
    br = RecordFilter.find_closest_record(brs, datetime_time, SVN)
    # (1)Time from ephemeris epoch toe
    tk = time.GpsSecond - br.toe
    # (2)Calculate the semimajor axis
    a = br.sqrt_a ** 2
    # (3)Compute mean motion – rad/s
    n0 = math.sqrt(miu / a ** 3)
    # (4)Correct mean motion
    n = n0 + br.delta_n
    # (5)Mean anomaly Mk at epoch t
    Mk = br.M0 + n * tk
    # (6)Eccentricity anomaly Ek at epoch t
    Ek = cal_Ek(Mk, br.e)
    # 计算钟差偏移和漂移部分
    clockerror_biasdrift = br.a0 + br.a1 * tk + br.a2 * tk ** 2
    # 计算钟差相对论效应部分
    clockerror_re = -4.443e-10 * br.e * math.sqrt(a) * math.sin(Ek)
    # 合并钟差
    clockerror = clockerror_biasdrift + clockerror_re
    return clockerror


if __name__ == "__main__":
    pass


