import os
import cv2
import albumentations as A
from tqdm import tqdm
import numpy as np

# 데이터 폴더와 결과를 저장할 폴더 경로 설정
data_folder = 'data'
output_folder = 'augmented_data'

# 클래스별로 결과를 저장할 폴더 생성
output_classes = ['can', 'plastic', 'paper', 'others']
for class_name in output_classes:
    os.makedirs(os.path.join(output_folder, class_name), exist_ok=True)


def slice_and_shuffle_horizontal(image, num_slices=None, **kwargs):
    # 이미지의 높이와 너비 가져오기
    height, width = image.shape[:2]
    
    # num_slices가 None이면 랜덤하게 설정
    if num_slices is None:
        num_slices = np.random.randint(2, 31)  # 2에서 30 사이의 랜덤한 값 설정
    
    # 이미지를 num_slices 조각으로 자르기
    slice_width = width // num_slices
    slices = [image[:, i*slice_width:(i+1)*slice_width] for i in range(num_slices)]
    
    # 자른 이미지를 랜덤하게 섞기
    np.random.shuffle(slices)
    
    # 이미지 다시 조합
    shuffled_image = np.concatenate(slices, axis=1)
    
    return shuffled_image



# Albumentations 변환 설정
transform = A.Compose([
    A.Lambda(image=slice_and_shuffle_horizontal, p= 1),
    A.HorizontalFlip(p=0.2),
    A.ElasticTransform(alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03, p=0.001),
    # A.OneOf([
    #     A.Transpose(p=0.01),
    #     A.VerticalFlip(p=0.01),
    #     A.RandomCrop(width=216, height=216, p=0.13),
    #     A.RandomBrightnessContrast(brightness_limit=(-0.2, 0.2), contrast_limit=(-0.2, 0.2), p=0.1),
    #     A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.125),
    #     A.ElasticTransform(alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03, p=0.005),
    #     A.OpticalDistortion(distort_limit=2, shift_limit=0.5, p=0.005),
    #     A.HorizontalFlip(p=0.235),
    # ], p = 1.0)
])

# 클래스별로 생성할 이미지 개수 설정
num_images_per_class = 5000

# # 데이터 폴더 탐색
# for class_name in output_classes:
#     class_folder = os.path.join(data_folder, class_name)
#     output_class_folder = os.path.join(output_folder, class_name)
    
#     # 이미지 파일 목록 가져오기
#     image_files = os.listdir(class_folder)
#     num_images_available = len(image_files)
    
#     # 이미지 반복해서 생성
#     for i in tqdm(range(num_images_per_class), desc=class_name):
#         # 이미지 선택
#         filename = image_files[i % num_images_available]
        
#         # 이미지 불러오기
#         image = cv2.imread(os.path.join(class_folder, filename))
        
#         # Albumentations 적용
#         augmented = transform(image=image)
#         augmented_image = augmented["image"]
        
#         # 저장
#         cv2.imwrite(os.path.join(output_class_folder, f"augmented_{i}.jpg"), augmented_image)


# 클래스별로 생성된 이미지 파일 목록을 저장할 딕셔너리
generated_images = {class_name: set() for class_name in output_classes}

# 데이터 폴더 탐색
for class_name in output_classes:
    class_folder = os.path.join(data_folder, class_name)
    output_class_folder = os.path.join(output_folder, class_name)
    
    # 이미지 파일 목록 가져오기
    image_files = os.listdir(class_folder)
    num_images_available = len(image_files)
    
    # 이미지 반복해서 생성
    for i in tqdm(range(num_images_per_class), desc=class_name):
        # 이미지 선택
        filename = image_files[i % num_images_available]
        
        # 이미지 불러오기
        image = cv2.imread(os.path.join(class_folder, filename))
        
        # Albumentations 적용
        augmented = transform(image=image)
        augmented_image = augmented["image"]
        
        # 저장
        output_filename = f"augmented_{i}.jpg"
        output_path = os.path.join(output_class_folder, output_filename)
        
        # 이미지가 중복되지 않으면 저장
        if output_filename not in generated_images[class_name]:
            cv2.imwrite(output_path, augmented_image)
            generated_images[class_name].add(output_filename)
