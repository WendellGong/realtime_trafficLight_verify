#图像实时输出ocr
import cv2
from PIL import Image
import tesserocr
import torch

cap = cv2.VideoCapture('v44_11011500581314005452_20230827053000_20230827054500.mp4')
output_file_path = "C://Users//duanh//ocr识别结果.txt"

roi_top = 0
roi_bot = 100
roi_left = 1500
roi_right = 2500
roi_time_para = {'roi_top':0, 'roi_bot':100, 'roi_left':1500, 'roi_right':2500}

roi_district_para = {'roi_top':850, 'roi_bot':1200, 'roi_left':1200, 'roi_right':2500}

def recognize_text_from_pil_image(pil_image):
    # 使用tesserocr从PIL图像中提取文字
    text = tesserocr.image_to_text(pil_image)
    return text


def main():
    print(torch.cuda.is_available())  # 查看CUDA是否可用
    print(torch.cuda.device_count())  # 查看可用的CUDA数量
    print(torch.version.cuda)  # 查看CUDA的版本号

    while True:
        ret, frame = cap.read()

        # 检查是否读取到帧
        if not ret:
            break
        with open(output_file_path, "a", encoding="utf-8") as out_file:

            frame = cv2.resize(frame, (1920, 1080))
            frame1 = cv2.resize(frame, (960, 540))
            cv2.imshow('original Image', frame1)
            time_roi = frame[roi_top:roi_bot, roi_left:roi_right]
            # district_roi = frame[roi_district_para['roi_top']:roi_district_para['roi_bot'],
            #                      roi_district_para['roi_left']:roi_district_para['roi_right']]

            img_gray = cv2.cvtColor(time_roi, cv2.COLOR_BGR2GRAY)
            threshold = 120
            _, img_binarized = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
            pil_img = Image.fromarray(img_binarized)

            extracted_text = recognize_text_from_pil_image(pil_img)
            print(f"从图像中识别的文字：\n{extracted_text}")

            out_file.write(f"{extracted_text}")

            cv2.imshow('filted time Image', time_roi)
            cv2.imshow('Processed time Image', img_binarized)

        # 此处可以添加其他处理代码，例如hsv_mask和box_visualization函数

        # 使用q键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()