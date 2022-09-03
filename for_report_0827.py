

import utils.DoFile as DoFile
import utils.PictureResults as PictureResults
import utils.ResultAnalyse as ResultAnalyse


posfile=''
pos_records = DoFile.read_posfile_xyz(r"D:\Desktop\8.27汇报\数据\zimm3100_1fre_unfixed.pos", 0, 0)
true_coor=[4331297.3480, 567555.6390, 4633133.7280]   #zimm
# true_coor=[3658785.6000, 784471.1000, 5147870.7000]   #warn

delta_ns, delta_es, delta_us=PictureResults.plot_poscoorres_neu(pos_records, true_coor)
print("neu各方向RMSE:", ResultAnalyse.get_NEU_rmse_2(delta_ns, delta_es, delta_us))

# pos_records = DoFile.read_posfile_xyz(r"D:\Desktop\8.27汇报\数据\zimm3100_1fre_unfixed.pos", 0, 0)
# print(ResultAnalyse.get_NEU_rmse([true_coor for i in range(len(pos_records))], [pos_record.pos_value for pos_record in pos_records]))



