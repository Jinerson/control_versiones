import time
import sys
from openai import APIConnectionError
from openai import OpenAI
from proyecto_1.config import API_KEY
from proyecto_1.modules.loggers import logger
from proyecto_1.modules.assistants import PersonalAssistant, AssistantManager
from proyecto_1.config import REPO_URL_T
from proyecto_1.modules.paths import BASE_DIR, RESULTS_DIR
from proyecto_1.modules.functions import temp_file, config_git, git_commit_and_push

def main():
    try:
        logger.info("Iniciando ejecucion principal para monitoreo de asistentes OpenAI...")
        #_ = internet_conn()
        # Crear y cargar un asistente de OpenAI y cargar su configuracion
        client = OpenAI(api_key=API_KEY) #Definir el cliente usando la APY_KEY
        assistant_manager = AssistantManager(client= client) # Crear objeto para manejar asistentes
        current_assistants = [key for key in assistant_manager.list_assistants()] # Crear lista de asistentes
    
        for assistant_id in current_assistants: #Iterar a traves de los asistentes
            assistant = PersonalAssistant() #Inicializar objeto asistente
            assistant.attach_client(client= client) #Asociar el asistente a un cliente
            assistant.load_from_api(assistant_id= assistant_id) #Cargar asistente desde la API
            logger.info(f"Cliente {assistant_id[0:5]}... cargado con exito.")
            assistant_config = assistant.get_assistant_config() #Cargar la configuracion del asistente actual
            logger.info(f"Configuracion de {assistant_id[0:5]}... cargado con exito.")

            # Guardar configuracion y prompt del asistente actual en archivo que sera temporal
            assistant_folder = RESULTS_DIR / f"{assistant_id}" # Carpeta para guardar archivo config.json y prompt.md del asistente
            assistant_folder.mkdir(parents= True, exist_ok= True) # Asegurar existencia de la carpeta.

            # Crear los archivos con configuracion del asistente.
            temp_file(assistant_folder /"config.json", 
                    assistant_folder / "prompt.md",
                    assistant_config) 
            time.sleep(3)

            # Iniciar cargado a github
            config_git(BASE_DIR, REPO_URL_T)
            git_commit_and_push(BASE_DIR, BASE_DIR, "Commit realizado")
            time.sleep(3)
    except APIConnectionError:
        logger.error("Verifique su conexion a internet.")
        sys.exit()
if __name__ == "__main__":
    main()
