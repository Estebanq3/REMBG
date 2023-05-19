from rembg import remove
from PIL import Image
import multiprocessing
from joblib import Parallel, delayed
import argparse
import datetime
import shutil
import re
import os

"""
    Variables estáticas globales (define)
"""
OUTPUT_IMAGES_DIRECTORY = str(datetime.datetime.now())
OUTPUT_IMAGES_DIRECTORY = re.sub(r"[^0-9]", "", OUTPUT_IMAGES_DIRECTORY)
os.makedirs(OUTPUT_IMAGES_DIRECTORY)
OUTPUT_IMAGES_DIRECTORY += "/"

#INPUT_IMAGES_DIRECTORY = './input_images/'
BACKGROUND_IMAGES_DIRECTORY = './backgrounds/'
MERGE_IMAGES_DIRECTORY = './rembg_results/'
OUTPUT_PREFIX_NAME = 'rembg_'
MERGE_PREFIX_NAME = 'merge_'


"""
    Obtiene todos los archivos que se encuentran en un directorio.

    Parámetros:
    - directory: el directorio donde se encuentran todos los archivos.

    Retorna:
    - list, un listado de todos los archivos que se encuentran en el directorio.
"""
def get_files_in_directory(directory):

    files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            files.append(file)
    return files

"""
    Toma un input como imagen y recorta a las personas que se encuentran para posteriormente generar una imagen sin fondo de las personas. Si son varias personas retorna solo una imagen con todas las personas.

    Parámetros:
    - input_images_directory: el directorio donde se encuentran las imágenes.
    - file: la imagen que se va a procesar.

    Retorna:
    - No retorna nada, mas si genera una imagen como output, la cual es la persona o personas recortadas en un fondo transparente.
"""
def generate_images_w_background(input_images_directory, file):
    with open(input_images_directory + file, 'rb') as i:
        print(OUTPUT_IMAGES_DIRECTORY)
        with open(OUTPUT_IMAGES_DIRECTORY + OUTPUT_PREFIX_NAME + file.split(".")[0] + ".jpg", 'wb') as o:
            input = i.read()
            output = remove(input)
            o.write(output)

"""
    Ciclo para rellenar una lista con números que representan cada una de las imágenes existentes en un directorio.

    Parámetros:
    - files: imágenes de un directorio pero ya se pasan en una lista.

    Retorna:
    - list, lista con los índices numéricos que representan cada imagen.
"""
def loop_files(files):
    list_index = []
    i = 0
    for file in files:
        list_index.append(i)
        i += 1

    return list_index

"""
    Fusiona una imagen recortada, es decir de una persona recortada con un fondo.

    Parámetros:
    - background_name: el nombre del fondo.
    - image_name: el nombre de la imagen recortada.

    Retorna:
    - No retorna nada, mas si genera el fotomontaje de la imagen recortada fusionada con el fondo.
"""
def merge_image_background(background_name, image_name):
    # Open the background image
    background = Image.open(BACKGROUND_IMAGES_DIRECTORY + background_name, 'r')

    # Open the image with transparent background
    image = Image.open(OUTPUT_IMAGES_DIRECTORY + image_name, 'r')

        
    #print(image_name)

    # Resize the image to fit within the background
    #image = image.resize(background.size)  # Adjust the size as needed

    # Specify the position to insert the image onto the background
    position = (int(background.width // 2)-int(image.width // 2), int(background.height // 1.5) - int(image.height // 2))  # Adjust the coordinates as needed

    # Create a composite image by pasting the image onto a transparent background
    composite = Image.new("RGBA", background.size)
    composite.paste(background, (0, 0))
    composite.paste(image, position, mask=image)

    #compose new name
    background_name = background_name.split(".")[0]

    image_name = image_name.split(".")[0]

    #Estampa de tiempo
    time_stamp_differentiator = str(datetime.datetime.now())
    time_stamp_differentiator = re.sub(r"[^0-9]", "", OUTPUT_IMAGES_DIRECTORY)

    # Save the resulting image
    composite.save(MERGE_IMAGES_DIRECTORY + background_name + '_' + image_name + time_stamp_differentiator + '.png')

    return "Finalizado con exito"

"""
    Fusiona una imagen recortada con múltiples fondos.

    Parámetros:
    - backgrounds: la lista de los fondos con los que la imagen recortada se va a fusionar.
    - image_name: el nombre de la imagen recortada.

    Retorna:
    - No retorna nada, mas si genera los fotomontajes de la imagen recortada fusionada con los fondos.
"""
def image_with_many_backgrounds(backgrounds, image_name):
    for i in backgrounds:
        merge_image_background(i,image_name)


def parallelize_generate_images_w_background(input_images_directory):
    images_files = get_files_in_directory(input_images_directory)
    index_images = loop_files(images_files)
    n_jobs = multiprocessing.cpu_count()
    Parallel(n_jobs=n_jobs)(delayed(generate_images_w_background)(input_images_directory, i) for i in images_files)
    rembg_files = get_files_in_directory(OUTPUT_IMAGES_DIRECTORY)
    return  n_jobs,index_images,rembg_files


def main(input_directory, unique_background, background):
    if unique_background == "True":
        n_jobs,index_images,rembg_files = parallelize_generate_images_w_background(input_directory)
        Parallel(n_jobs=n_jobs)(delayed(merge_image_background)(background,rembg_files[j]) for j in index_images)
    else:
        n_jobs,index_images,rembg_files = parallelize_generate_images_w_background(input_directory)
        Parallel(n_jobs=n_jobs)(delayed(image_with_many_backgrounds)(background,rembg_files[j]) for j in index_images)
    
    shutil.rmtree(OUTPUT_IMAGES_DIRECTORY)


if __name__ == "__main__":
    parser = argparse = argparse.ArgumentParser()
    parser.add_argument("--input_directory", help="Input images directory")
    parser.add_argument("--unique_background", type=bool, help="True if it is a unique background, false if not")
    parser.add_argument("--background", help="Background list in order of the images in the directory")
    
    args = parser.parse_args()

    args.background = args.background.split(",")

    main(args.input_directory ,args.unique_background, args.background)

