"""
@Project     :Script4JJ 
@File        :pic_classify.py
@IDE         :PyCharm 
@Author      :LYF
@Date        :2024/4/10 13:42
@Description :
"""

from PIL import Image
import tqdm
import os
import shutil

# 设置图片的源文件夹和目标文件夹
source_folder = 'pic/精修'
target_folders = {
    'landscape': 'result_select/横版',
    'portrait': 'result_select/竖版',
    'square': 'result_select/方版'
}

# 确保目标文件夹存在
for folder in target_folders.values():
    os.makedirs(folder, exist_ok=True)

# 遍历源文件夹中的所有文件
for filename in tqdm.tqdm(os.listdir(source_folder)):
    # 构建完整的文件路径
    file_path = os.path.join(source_folder, filename)

    # 检查文件是否是图片
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
        # 打开图片
        with Image.open(file_path) as img:
            # 获取图片的宽度和高度
            width, height = img.size

            # 根据纵横比分类图片
            if width > height:
                destination_folder = target_folders['landscape']
            elif width < height:
                destination_folder = target_folders['portrait']
            else:
                destination_folder = target_folders['square']

            # 构建目标文件路径
            dest_file_path = os.path.join(destination_folder, filename)

            # 将图片复制到目标文件夹
            shutil.copy2(file_path, dest_file_path)
            # print(dest_file_path)

        # 从源文件夹中删除已处理的图片（可选）
        # os.remove(file_path)

print("图片分类完成。")