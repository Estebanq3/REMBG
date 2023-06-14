from rembg import remove
from PIL import Image
import multiprocessing
from joblib import Parallel, delayed
import argparse
import datetime
import shutil
import re
import os
from fastapi import FastAPI

"""
    Variables estáticas globales (definicion)
"""
#INPUT_IMAGES_DIRECTORY = './input_images/'
#MERGE_IMAGES_DIRECTORY = './rembg_results/'
BACKGROUND_IMAGES_DIRECTORY = '../backgrounds/'
OUTPUT_PREFIX_NAME = 'rembg_'
MERGE_PREFIX_NAME = 'merge_'
TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT = './tmp_copia_local/'
TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT = './tmp_copia_automatica/'

"""
    Crea los directorio temporales donde se guardaran las fotos que seran procesadas con los backgrounds para realizar un fotomontaje

    Parámetros:
    
    Retorna:
    - string, el nombre del directorio temporal creado
"""
def create_output_directory():
    OUTPUT_IMAGES_DIRECTORY = str(datetime.datetime.now())
    OUTPUT_IMAGES_DIRECTORY = re.sub(r"[^0-9]", "", OUTPUT_IMAGES_DIRECTORY)
    os.makedirs(OUTPUT_IMAGES_DIRECTORY)
    OUTPUT_IMAGES_DIRECTORY += "/"
    
    return OUTPUT_IMAGES_DIRECTORY

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
def generate_images_w_background(input_images_directory, file, output_directory):
    with open(input_images_directory + file, 'rb') as i:
        #print(OUTPUT_IMAGES_DIRECTORY)
        with open(output_directory + OUTPUT_PREFIX_NAME + file.split(".")[0] + ".jpg", 'wb') as o:
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
def merge_image_background(background_name, image_name, output_directory, output_merge_results):
    # Open the background image
    background = Image.open(BACKGROUND_IMAGES_DIRECTORY + background_name, 'r')

    # Open the image with transparent background
    image = Image.open(output_directory + image_name, 'r')

        
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
    time_stamp_differentiator = re.sub(r"[^0-9]", "", output_directory)

    # Save the resulting image
    composite.save(output_merge_results + background_name + '_' + image_name + time_stamp_differentiator + '.png')

    return "Finalizado con exito"

"""
    Fusiona una imagen recortada con múltiples fondos.

    Parámetros:
    - backgrounds: la lista de los fondos con los que la imagen recortada se va a fusionar.
    - image_name: el nombre de la imagen recortada.

    Retorna:
    - No retorna nada, mas si genera los fotomontajes de la imagen recortada fusionada con los fondos.
"""
def image_with_many_backgrounds(backgrounds, image_name, output_directory, output_merge_results):
    for i in backgrounds:
        merge_image_background(i, image_name, output_directory, output_merge_results)

'''
    Paraleliza las tareas de hacer merge de las imagenes con los fondos

    Parámetros:
    - input_images_directory: el directorio donde se encuentran las imagenes a procesar.
    - output_directory: el directorio temporal donde se almacenan las imagenes recortadas antes de hacer el merge y procesarlas completamente.

    Retorna:
    - No retorna nada, mas si genera los fotomontajes de la imagen recortada fusionada con los fondos.
'''
def parallelize_generate_images_w_background(input_images_directory, output_directory):
    images_files = get_files_in_directory(input_images_directory)
    index_images = loop_files(images_files)
    # Definir el numero de hilos deseados y que soporta el servidor
    n_jobs = multiprocessing.cpu_count()
    Parallel(n_jobs=n_jobs)(delayed(generate_images_w_background)(input_images_directory, i, output_directory) for i in images_files)
    rembg_files = get_files_in_directory(output_directory)
    return  n_jobs,index_images,rembg_files


"""
   Main de la aplicacion, esta es llamada por el API de no ejecutarse mediante linea de comandos

    Parámetros:
    - input_directory: el directorio donde se encuentran las imagenes a procesar.
    - unique_background: 
        true: todas las fotos se procesaran con un unico background
        false: todas las fotos se procesaran con la lista de backgrounds que se pasen
    -background: background o lista de backgrounds a utilizar
    -ouput_merge_results: directorio donde se almacenaran los resultados del procesamiento de las fotos

    Retorna:
    - list, un listado de los nombres de todas las fotos que han sido procesadas
"""
def main(input_directory, unique_background, background, output_merge_results):
    #try:
        output_directory = create_output_directory()
        if unique_background == "True":
            n_jobs,index_images,rembg_files = parallelize_generate_images_w_background(input_directory, output_directory)
            Parallel(n_jobs=n_jobs)(delayed(merge_image_background)(background,rembg_files[j], output_directory) for j in index_images)
        else:
            n_jobs,index_images,rembg_files = parallelize_generate_images_w_background(input_directory, output_directory)
            Parallel(n_jobs=n_jobs)(delayed(image_with_many_backgrounds)(background,rembg_files[j], output_directory, output_merge_results) for j in index_images)

        shutil.rmtree(output_directory)
        
        #print("Todas las fotos han sido procesadas adecuadamente")

        return "Fotos procesadas:" + str(rembg_files)
    #except:
        #print("Error procesando las fotos")
    #   return "Fotos que no han podido ser procesadas"  + str(rembg_files)

if __name__ == "__main__":
    parser = argparse = argparse.ArgumentParser()
    parser.add_argument("--input_directory", help="Input images directory")
    parser.add_argument("--ouput_directory", help ="Output files directory")
    parser.add_argument("--unique_background", type=bool, help="True if it is a unique background, false if not")
    parser.add_argument("--background", help="Background list in order of the images in the directory")
    
    args = parser.parse_args()

    args.background = args.background.split(",")

    main(args.input_directory ,args.unique_background, args.background, args.ouput_directory)


