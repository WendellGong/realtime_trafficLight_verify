import numpy as up
import time

file_path = "66666.txt"

#jingzhiwang   UHD
def file_read():
    light_file = open(file_path, "r")

    for light_line in light_file:

        light_line = light_line[120:]
        print(light_line)
        assert light_line[0:2] == "C0"
        print("sent_id:", light_line[4:6] + light_line[2:4])

        district_code = light_line[10:12] + light_line[8:10] + light_line[6:8]
        district_code = bytes.fromhex(district_code)
        district_code = int.from_bytes(district_code, byteorder='big', signed=False)

        print("district_code", district_code)
        type_code = light_line[14:16] + light_line[12:14]
        if type_code == '1000':
            print("type_code", type_code, "Bit13：除信号机以外的其他路侧交通管控设备")
        id_code = light_line[16:20]
        print("id_code", id_code)
        recv_code = light_line[22:36]
        print("recv_code", recv_code)
        time_stamp = light_line[42:44] + light_line[40:42] + light_line[38:40] + light_line[36:38]
        print("time_stamp:", time_stamp)
        time_stamp = bytes.fromhex(time_stamp)
        time_stamp = int.from_bytes(time_stamp, byteorder='big', signed=False)
        time_stamp = time.localtime(time_stamp)
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S",time_stamp)

        print("time_stamp:", time_stamp)
        TTL = light_line[48:50]
        TTL = bytes.fromhex(TTL)
        TTL = int.from_bytes(TTL, byteorder='big', signed=False)
        print("TTL", TTL, " seconds")
        assert light_line[50:52] == "10"
        operation_type = light_line[52:54]
        if operation_type == "83":
            print("operation_type: ", operation_type, "对查询请求的应答")
        elif operation_type == "87":
            print("operation_type: ", operation_type, "广播数据")
        object_id = light_line[54:56] + light_line[56:58]
        if object_id == "0301":
            print("0301，当前信号方案色步信息:描述信号机当前运行方案的灯色及时长")
        elif object_id == "0103":
            print("0103，信号灯灯色状态:描述当前信号灯组的灯色和剩余时间")
        sign_mark = light_line[58:60]

        print("sign_mark: ", sign_mark)

        reserve = light_line[60:66]
        print("保留：", reserve)

        information_len = light_line[68:70] + light_line[66:68]
        print("消息长度：", information_len)

        longitude = light_line[76:78] + light_line[74:76] + light_line[72:74] + light_line[70:72]
        latitude = light_line[84:86] + light_line[82:84] + light_line[80:82] + light_line[78:80]
        altitude = light_line[88:90] + light_line[86:88]
        print("经度：", longitude)
        print("纬度：", latitude)
        print("海拔：", altitude)

        light_num = light_line[90:92]
        print("灯组数量：", light_num)
        x = 0


        for x in range(int(light_num)):
            en_direct = light_line[(94 + (x * 38)):(96 + (x * 38))] + light_line[(92 + (x * 38)):(94 + (x * 38))]
            print("进口方向：", en_direct)

            en_light_num = light_line[(96 + (x * 38)):(98 + (x * 38))]
            print("进口灯组数量：", en_light_num)

            for i in range(int(en_light_num)):
                light_set_num = light_line[(98 + (x * 38) + (i * 8)):(100 + (x * 38) + (i * 8))] #灯组编号
                light_set_type = light_line[(100 + (x * 38) + (i * 8)):(102 + (x * 38) + (i * 8))] #灯组类型
                color_step = light_line[(102 + (x * 38) + (i * 8)):(104 + (x * 38) + (i * 8))] #色步数
                light_color = light_line[(104 + (x * 38) + (i * 8)):(106 + (x * 38) + (i * 8))] #灯色

                if int(light_set_type) == 1:
                    light_set_type_name = "直行方向指示信号灯"
                elif int(light_set_type) == 2:
                    light_set_type_name = "左转方向指示信号灯"
                elif int(light_set_type) == 3:
                    light_set_type_name = "右转方向指示信号灯"
                elif int(light_set_type) == 4:
                    light_set_type_name = "机动车信号灯"
                elif int(light_set_type) == 5:
                    light_set_type_name = "左转非机动车信号灯"
                elif int(light_set_type) == 6:
                    light_set_type_name = "右转非机动车信号灯"
                elif int(light_set_type) == 7:
                    light_set_type_name = "非机动车信号灯"
                elif int(light_set_type) == 8:
                    light_set_type_name = "人行横道信号灯"
                elif int(light_set_type) == 9:
                    light_set_type_name = "掉头信号灯"
                elif int(light_set_type) == 10:
                    light_set_type_name = "车道信号灯"
                elif int(light_set_type) == 11:
                    light_set_type_name = "道口信号灯"
                elif int(light_set_type) == 12:
                    light_set_type_name = "闪光警告信号灯"
                elif int(light_set_type) == 13:
                    light_set_type_name = "有轨电车专用信号灯（直行）"
                elif int(light_set_type) == 14:
                    light_set_type_name = "有轨电车专用信号灯（左转）"
                elif int(light_set_type) == 15:
                    light_set_type_name = "有轨电车专用信号灯（右转）"   #这里的有点问题，每一次循环卡时间，可以改进一下
                else:
                    light_set_type_name = "wrong_type"

                int_judge_color = int(light_color, 16)
                bin_judge_color = bin(int_judge_color)[2:]
                bin_judge_color = bin_judge_color[::-1]

                if int(light_set_type) < 13:
                    colors = []
                    if bin_judge_color[0:2] == '01':
                        colors.append("红色亮")
                    if bin_judge_color[0:2] == '11':
                        colors.append("红色闪")
                    if bin_judge_color[0:2] == '10':
                        colors.append("红色灭")
                    if bin_judge_color[2:4] == '01':
                        colors.append("黄色亮")
                    if bin_judge_color[2:4] == '11':
                        colors.append("黄色闪")
                    if bin_judge_color[2:4] == '10':
                        colors.append("黄色灭")
                    if bin_judge_color[4:6] == '01':
                        colors.append("绿色亮")
                    if bin_judge_color[4:6] == '11':
                        colors.append("绿色闪")
                    if bin_judge_color[4:6] == '10':
                        colors.append("绿色灭")
                    if bin_judge_color[4:6] == '00' and bin_judge_color[2:4] == '00' and bin_judge_color[0:2] == '00':
                        colors.append("全灭")



                print("灯组编号：", light_set_num, " 灯组类型：", light_set_type_name, " 色步数：", color_step, "存在的颜色：", colors[::])

    light_file.close()



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_read()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
