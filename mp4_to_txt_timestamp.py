import cv2
import numpy as np
from PIL import Image
import tesserocr

# 更改为读取静态图片
image_path = "C://Users//duanh//Desktop//default.jpg"
output_file_path = "C://Users//duanh//Desktop//ocr识别结果.txt"

roi_top = 800
roi_bot = 1000
roi_left = 240
roi_right = 800

roi_top_2 = 155
roi_bot_2 = 260
roi_left_2 = 240
roi_right_2 = 725

def recognize_text_from_pil_image(pil_image):
    # 使用tesserocr从PIL图像中提取文字
    with tesserocr.PyTessBaseAPI() as api:
        api.SetVariable("tessedit_char_whitelist", "0123456789")  # 设置字符白名单
        api.SetVariable("tessedit_ocr_engine_mode", "3")  # 设置OCR引擎模式
        api.SetVariable("tessedit_pageseg_mode", "6")  # 设置页面分割模式
        api.SetImage(pil_image)
        text = api.GetUTF8Text()
    return text

def main():
    img = cv2.imread(image_path)
    img_2 = cv2.imread(image_path)

    # 检查是否成功加载图像
    if img is None:
        print("图像加载失败!")
        return

    with open(output_file_path, "a") as out_file:
        img = cv2.resize(img,(1000,1000))
        img_2 = cv2.resize(img_2,(1000,1000))

        M = np.ones(img.shape, dtype="uint8") * 100  # 增加亮度的量，可以根据需要进行调整
        brightened_img = cv2.add(img, M)

        M = np.ones(img_2.shape, dtype="uint8") * 100  # 增加亮度的量，可以根据需要进行调整
        brightened_img_2 = cv2.add(img_2, M)

        roi = brightened_img[roi_top:roi_bot, roi_left:roi_right]
        roi_2 = brightened_img_2[roi_top_2:roi_bot_2, roi_left_2:roi_right_2]

        img_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        img_2_gray = cv2.cvtColor(roi_2, cv2.COLOR_BGR2GRAY)
        threshold = 130
        threshold_2 = 110
        _, img_binarized = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
        _, img_2_binarized = cv2.threshold(img_2_gray, threshold_2, 255, cv2.THRESH_BINARY)
        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))#膨胀
        kernel_dilate_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))#膨胀
        kernel_dilate_3 = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        kernel_dilate_4 = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6))
        img_dilate = cv2.dilate(img_binarized, kernel_dilate, iterations=1)
        img_2_dilate = cv2.erode(img_2_binarized, kernel_dilate_3,iterations=1)
        img_2_dilate = cv2.dilate(img_2_dilate, kernel_dilate_2, iterations=1)
        img_2_dilate = cv2.dilate(img_2_dilate, kernel_dilate_4, iterations=1)
        img_dilated = cv2.bitwise_not(img_dilate)
        img_2_dilate = cv2.bitwise_not(img_2_dilate)
        pil_img = Image.fromarray(img_dilate)
        pil_2_img = Image.fromarray(img_2_dilate)

        extracted_text = recognize_text_from_pil_image(pil_img)
        extracted_text_2 = recognize_text_from_pil_image(pil_2_img)
        print(f"从图像中识别上面的文字：\n{extracted_text}")
        print(f"从图像中识别下面的文字：\n{extracted_text_2}")
        out_file.write(f"{extracted_text}")

        # 此处可以添加其他处理代码，例如显示处理后的图片
        cv2.imshow('Processed Image', img_dilated)
        cv2.imshow('down image', img_2_dilate)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()