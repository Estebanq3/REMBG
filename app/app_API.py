from fastapi import FastAPI
from remove_background_automatized import *

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
    Utilizacion de FastApi para poder hacer un call de la funcion de procesamiento de imagenenes en la direccion root
'''
@app.get("/")
def call():

    backgrounds_list = get_image_names(BACKGROUNDS)
    files_processed = []
    
    #obtener los directorios que se encuentren en tmp_copia_local
    directories = get_directory_names(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT[:-1])
    
    #  Ciclo para tmp_copia_local
    for i in directories:
        #Si existe un ouput ya creado por un run anterior elimina el output
        if os.path.exists(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output'):
            shutil.rmtree(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output')
        #Crea el directorio output nuevo
        os.makedirs(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output')
        files_processed.append(main(TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + i,False, backgrounds_list, TMP_COPIA_LOCAL_EACH_DIRECTORY_OUTPUT + i + OUTPUT_MERGE)) 

    #obtener los directorios que se encuentren en tmp_copia_automatica
    directories = get_directory_names(TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT[:-1])

    #   Ciclo para tmp_copia_automatica
    for i in directories:
        #Si existe un ouput ya creado por un run anterior elimina el output
        if os.path.exists(TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output'):
            shutil.rmtree(TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output')
        #Crea el directorio output nuevo
        os.makedirs(TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT + '/' + i + '/Output')
        files_processed.append(main(TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT + i,False, backgrounds_list, TMP_COPIA_AUTOMATICA_EACH_DIRECTORY_OUTPUT + i + OUTPUT_MERGE)) 

    return files_processed

