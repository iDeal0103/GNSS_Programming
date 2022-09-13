# -*- coding: utf-8 -*-
"""

@title:	rtkcmn
@author: iDeal0103
@status:	Active
@type:	Process
@created:	9-Spt-2022
@post-History:	9-Spt-2022

comment:
    1. 关于rtk处理的处理设置参数
    2. debug相关参数设置

"""

#
class process_opt:
    def __init__(self):
        self.pr_sigma = 3      # 伪距观测值标准差，单位为m
        self.cp_sigma = 0.3      # 载波相位观测值标准差，单位为cycle
        self.frequecy = 1        # 参与解算的频率   1:L1  2:L1+L5
        self.bl_constrain = False      # 是否附加基线长约束
        self.bl_sigma = 0.1          # 基线长标准差，单位为m

