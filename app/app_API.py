from fastapi import FastAPI
from remove_background_automatized import *
from fastapi.params import Depends, Query

#Variables globales para definir el API, asi como para definir los directorios
app = FastAPI()
TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT = '../tmp_copia_local/'
TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT = '../tmp_copia_automatica/'
OUTPUT_MERGE = '/Output/'
BACKGROUNDS = '../backgrounds'

'''
    Funcion para obtener los directorios tanto de tmpcopialocal como de tmpcopiaautomatica
'''
def get_directory_names(directory):
    directory_names = []
    for entry in os.scandir(directory):
        if entry.is_dir():
            directory_names.append(entry.name + '/')
    return directory_names


def get_image_names(directory):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']  # Add or remove extensions as needed
    image_names = []
    
    for file_name in os.listdir(directory):
        if any(file_name.lower().endswith(ext) for ext in image_extensions):
            image_names.append(file_name)
    
    print(image_names)
    return image_names

'''
    Funcion para eliminar todas las imagenes de una carpeta
'''
def delete_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if "rembg" in file:
                return True
            else:
                file_path = os.path.join(root, file)
                os.remove(file_path)

'''
    Utilizacion de FastApi para poder hacer un call de la funcion de procesamiento de imagenenes en la direccion root
'''
@app.get("/fastApi/v1/rembg/")
def call(input_directory: str):
    try:
        backgrounds_list = get_image_names(BACKGROUNDS)
        files_processed = []
        files_processed.append(main(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + input_directory,False, backgrounds_list, TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + input_directory)) 
        delete_files_in_directory(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + input_directory)
        return "Se han añadido a la lista nuevas fotos por procesar"
    except:
        return "Error: No se han añadido a la lista nuevas fotos por procesar"
    

