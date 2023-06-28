from rembg import remove
import cv2
import glob
import os

input_folder = 'C:\images'
output_folder = 'C:\output'

# Membuat folder output jika belum ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Melakukan loop pada semua file gambar dalam folder input yang memiliki ekstensi ".jpg"
for img_path in glob.glob(os.path.join(input_folder, '*.jpg')):
    # Mendapatkan nama file
    file_name = os.path.basename(img_path)
    # Mendapatkan nama file tanpa ekstensi
    file_name_no_ext = os.path.splitext(file_name)[0]

    try:
        # Membaca gambar menggunakan OpenCV
        cv_img = cv2.imread(img_path)

        # Menghapus latar belakang menggunakan rembg
        output = remove(cv_img)

        # Menyimpan gambar dengan latar belakang yang dihapus ke folder output dalam format PNG
        output_path = os.path.join(output_folder, file_name_no_ext + '.png')
        cv2.imwrite(output_path, output)
    except Exception as e:
        print(f"Error processing image {file_name}: {e}")

    print(f"Image {file_name} processed.")

print("All images processed.")