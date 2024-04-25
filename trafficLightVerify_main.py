#这个程序是针对路侧视频将视频中的信息进行提取，灯色和时间戳这两部分
#目前这个工作还没做完，你主要看这个就行



import re
import cv2 #opencv库
import numpy as np
from PIL import Image
import tesserocr #ocr库 用于文字识别

cap = cv2.VideoCapture('v44_11011500581314005452_20230827053000_20230827054500.mp4')
output_file_path = "C://Users//duanh//Desktop//视频单个灯色实时输出.txt"

roi_top = 50
roi_bot = 180
roi_left = 2240
roi_right = 2300 #设定好红绿灯区域

roi_top_ocr = 135
roi_bot_ocr = 210
roi_left_ocr = 3248
roi_right_ocr = 4032 #设定好时间戳文字识别区域

previous_hour = None
previous_minute = None
previous_second = None
previous_result = None #没用

def hsv_mask(frame): #RGB色域转换位HSV色域
    frame = cv2.resize(frame, (4096, 2160))
    frame_ocr = cv2.resize(frame, (4096, 2160))
    # 截取roi区域
    roiColor = frame[roi_top:roi_bot, roi_left:roi_right]
    # 转换hsv颜色空间
    kernel = np.ones((3,3), np.uint8)
    hsv = cv2.cvtColor(roiColor, cv2.COLOR_BGR2HSV)
    lower_hsv_red1 = np.array([0, 50, 50])
    upper_hsv_red1 = np.array([8, 255, 255])
    mask_red = cv2.inRange(hsv, lowerb=lower_hsv_red1, upperb=upper_hsv_red1)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

    # 中值滤波
    red_blur = cv2.medianBlur(mask_red, 7)

    # red another
    lower_hsv_red2 = np.array([172, 50, 50])
    upper_hsv_red2 = np.array([179, 255, 255])
    mask_red = cv2.inRange(hsv, lowerb=lower_hsv_red2, upperb=upper_hsv_red2)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)

    #中值滤波
    red_blur2 = cv2.medianBlur(mask_red, 7)


    # yellow
    lower_hsv_yellow = np.array([20, 50, 50])
    upper_hsv_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lowerb=lower_hsv_yellow, upperb=upper_hsv_yellow)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)


    # 中值滤波
    yellow_blur = cv2.medianBlur(mask_yellow, 7)

    # green
    lower_hsv_green = np.array([35, 30, 30])
    upper_hsv_green = np.array([85, 255, 255])
    mask_green = cv2.inRange(hsv, lowerb=lower_hsv_green, upperb=upper_hsv_green)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

    # 中值滤波
    green_blur = cv2.medianBlur(mask_green, 7)
    # green_blur = mask_green

    return red_blur, yellow_blur, green_blur, red_blur2

def recognize_text_from_pil_image(pil_image): # 时间戳文字识别
    global previous_hour, previous_minute, previous_second, previous_result
    # 使用tesserocr从PIL图像中提取文字
    with tesserocr.PyTessBaseAPI() as api:
        api.SetVariable("tessedit_char_whitelist", "0123456789")  # 设置字符白名单
        api.SetVariable("tessedit_ocr_engine_mode", "3")  # 设置OCR引擎模式
        api.SetVariable("tessedit_pageseg_mode", "6")  # 设置页面分割模式
        api.SetImage(pil_image)
        text = api.GetUTF8Text().strip()   # 这部分都是限定时间戳读取为数字，防止出现识别乱码

        # 正则表达式
        pattern = r"^(\d{4})(\d{2,3})(\d{2})(\d{2})(\d{2})(\d{2})$"
        match = re.search(pattern, text) # 正则表达式为了使时间识别出来为固定的2023-08-23 11:11:11格式
        if match:
            year, month, day, hour, minute, second = match.groups()
            if year != ["2023"]:
                year = "2023"
            # 如果月份是06或068，修正为08
            if month != ["08"]:
                month = "08"
            if day != ["27"]:
                day = "27"

            if hour != "05":
                hour = "05"

            if not (28 <= int(minute) <= 59):
                minute = previous_minute

            if previous_second == "59" and second == "00":
                second = "00"
            elif previous_second and (int(second) < int(previous_second) or (
                    int(second) - int(previous_second)) > 2):
                second = previous_second   # 这部分是为了限定，限定几个固定的数字，比如月份是八月份



            # 如果上次的小时和分钟存在，并且当前识别到的与上次的差值大于2
            if previous_hour and previous_minute:
                if abs(int(hour) - int(previous_hour)) > 1 or abs(int(minute) - int(previous_minute)) > 2:
                    hour, minute = previous_hour, previous_minute
            # 更新上次的小时和分钟
            previous_hour, previous_minute, previous_second = hour, minute, second

            text = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second) # 这部分是用了逻辑的方法来固定时间

            previous_result = text
        else:
            text = previous_result


    return text


def box_visualization(frame, red_blur, yellow_blur, green_blur, red_blur2): # 判断hsv色域的灯色 利用像素的个数
    # 设置一个阈值，如500，根据实际情况调整
    threshold = 500 # 这个阈值要实时调整，根据整个视频的背景光照变化 需要自适应的调整

    with open(output_file_path, "a", encoding="utf-8") as out_file:
        red_count = cv2.countNonZero(red_blur)
        yellow_count = cv2.countNonZero(yellow_blur)
        green_count = cv2.countNonZero(green_blur)
        red_count2 = cv2.countNonZero(red_blur2) #红绿黄像素数量

        # 在red_count中判断，如果数值大于threshold，那么就判定为red
        # 逻辑判断 很容易理解，因为容易出现红色和黄色混着的情况
        if red_count > threshold:
            if yellow_count < threshold:
                cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
                cv2.putText(frame, "red", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                a = "red"
            elif yellow_count > threshold:
                cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
                cv2.putText(frame, "yellow", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                a = "yellow"
        elif red_count2 > threshold:
            if yellow_count < threshold:
                cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
                cv2.putText(frame, "red", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                a = "red"
            elif yellow_count > threshold:
                cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
                cv2.putText(frame, "yellow", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                a = "yellow"
        elif yellow_count > threshold:
            cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
            cv2.putText(frame, "yellow", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            a = "yellow"
        elif green_count > threshold:
            cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255), 2)
            cv2.putText(frame, "green", (roi_right, roi_bot), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            a = "green"
        else:
            a = "none"

        roi_ocr = frame[roi_top_ocr:roi_bot_ocr, roi_left_ocr:roi_right_ocr]  # 设定ocr区域
        roi_ocr = cv2.convertScaleAbs(roi_ocr, alpha=1.5, beta=50)  # 增加亮度
        img_gray = cv2.cvtColor(roi_ocr, cv2.COLOR_BGR2GRAY)  # 灰度转换
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)  # 高斯滤波

        threshold_ocr = 200
        _, img_binarized = cv2.threshold(img_gray, threshold_ocr, 255, cv2.THRESH_BINARY)  # 转换为二值图像

        pil_img = Image.fromarray(img_binarized)
        extracted_text = recognize_text_from_pil_image(pil_img)
        cv2.imshow('a', img_binarized)
        print(f"从图像中识别的文字：\n{extracted_text}")  # 输出图像文字和颜色
        print(a)
        out_file.write(f"{extracted_text}")

        out_file.write(f"{a}\n")  # 文件写入
        cv2.namedWindow('frame', cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow('frame', 1000, 500)
        cv2.imshow('frame', frame)
        red_blur = cv2.resize(red_blur, (300, 200))
        yellow_blur = cv2.resize(yellow_blur, (300, 200))
        green_blur = cv2.resize(green_blur, (300, 200))
        cv2.imshow('red_window', red_blur)
        cv2.imshow('yellow_window', yellow_blur)
        cv2.imshow('green_window', green_blur)  # 窗口设定


def main():
    frame_counter = 0
    while True:
        ret,frame = cap.read()
        if ret == False:
            break

        frame_counter += 1
        # print(int(frame_counter) / 25)
        # 这部分是这样的 利用ocr识别时间戳有的时候背景颜色太亮可能效果不好，我提出了利用帧数限定时间从而判断时间戳，你根据这个思路改进一下，

        if frame_counter > 600 * 25: #为了快进，其中1就是1秒，你可以多快进一些秒数，从而判断后面的情况
            cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bot), (0, 0, 255),2)  # 按坐标画出矩形框
            red_blur, yellow_blur, green_blur, red_blur2 = hsv_mask(frame)
            box_visualization(frame, red_blur, yellow_blur, green_blur, red_blur2)

            c = cv2.waitKey(1)
            if c==27:
                break


if __name__ == '__main__':
    main()

