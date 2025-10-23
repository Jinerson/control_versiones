# src/proyecto_1/modules/assistants.py
import time
import datetime
import sys
import json
from openai import OpenAI
from openai.types.beta import Thread
from pydantic import BaseModel
from typing import Optional
from proyecto_1.modules.loggers import logger
from openai import APIConnectionError, AuthenticationError, NotFoundError

class PersonalAssistant(BaseModel):
    """Representa un asistente individual."""
    model_config = {"arbitrary_types_allowed": True} #Para evitar errores por tipos de datos no nativos de BaseModel
    id: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    temperature: Optional[float] = 0.0
    top_p: Optional[float] = 1.0

    client: Optional[OpenAI] = None
    thread: Optional[Thread] = None
    conversation: Optional[str] = None

    def attach_client(self, client: OpenAI):
        self.client = client
        logger.info("Cliente asociado exitosamente.")

    def create_assistant(self, **kwargs):
        '''
        Parametros por defecto para crear el asistente.

        **Kwargs: 
            name: "Default_Assistant"
            model: "gpt-4o-mini"
            instructions: "You are a helpful assistant"
            description: ""
            temperature: 0.0
            top_p: 1.0
        '''
        if not self.client:
            logger.error("Se debe asociar un cliente antes de crear el asistente")
            return False
        kwargs.setdefault("name", "Default_Assistant")
        kwargs.setdefault("model", "gpt-4o-mini")
        kwargs.setdefault("instructions", "You are a helpful assistant")
        kwargs.setdefault("description", "")
        kwargs.setdefault("temperature", 0.0)
        
        try:
            response = self.client.beta.assistants.create(**kwargs)
            self.id = response.id
            logger.info("Assistente creado exitosamente. Id: %s", self.id)
            return response
        except Exception as e:
            logger.error("Error al crear el asistente.", exc_info= e)
            return False

    def load_from_api(self, assistant_id: str):
        if not self.client:
            logger.error("Se debe asociar un cliente (attach_client()) antes de crear el asistente.")
            sys.exit()
            return False
        try:
            data = self.client.beta.assistants.retrieve(assistant_id)
            self.id = data.id
            self.name = data.name
            self.model = data.model
            self.description = data.description
            self.instructions = data.instructions
            logger.info("Aistente %s cargado con exito.", self.id)
            return data
        except APIConnectionError:
            logger.error("No hay conexion a internet. Deteniendo ejecución.")
            sys.exit()
            return False
        except AuthenticationError:
            logger.error("La API_KEY usada no es valida, o no se tienen acceso al asistente.")
            sys.exit()
            return False
        except NotFoundError:
            logger.error("El asistente %s no existe.", assistant_id)
            sys.exit()
            return False
        except Exception as e:
            logger.error("No se pudo cargar el asistente.", exc_info= e)
            sys.exit()
            return False
        
    def send_message(self, message:str, espera_maixma = 300) -> None:

        try:
            # Crear hilo de conversacion.
            self.thread = self.client.beta.threads.create()
            logger.info("Thread creado, id: %s", self.thread.id)
        except Exception as e:
            logger.error("Error al crear un Thread del asistente.")

        try:
            # Agregar mensaje al hilo
            self.client.beta.threads.messages.create(
                thread_id = self.thread.id,
                role = "user",
                content = message)
            
            # Ejecutar hilo
            run = self.client.beta.threads.runs.create(
                thread_id = self.thread.id,
                assistant_id = self.id
            )
            logger.info("Mensaje de usuario enviado en el run: %s", run.id)
        except Exception as e:
            logger.error("Error al ejecutar el hilo de conversacion. Verificar el numero de tokens del modelo actual.", exc_info= e)
        
        logger.info("Esperando respuesta del asistente...")
        inicio = time.time()
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id = self.thread.id,
                run_id = run.id
            )
            logger.info("Estado del run: %s", run_status.status)
            
            if run_status.status.lower() in ["completed", "failed"]:
                break
            elif time.time() - inicio >= espera_maixma:
                logger.error(f"No se obtuvo respuesta del asistente en {espera_maixma/60} minuto/s.")
                sys.exit()
            time.sleep(1)

    def get_conversation(self) -> dict:
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        conversation = [
            {
            'role': msg.role, 
            'content': msg.content[0].text.value if msg.content else "Nothing...",
            'created_at': msg.created_at 
            } 
            for msg in reversed(messages.data)
            ]
        self.conversation = conversation
        return self.conversation

    def get_assistant_config(self) -> dict | None:
        """
        Retorna la configuración completa del asistente en formato dict,
        obtenida directamente desde la API de OpenAI.
        Incluye la fecha de última modificación legible si está disponible.
        """
        if not self.client:
            logger.error("Client not attached. Use attach_client() first.")
            sys.exit()
        if not self.id:
            logger.error("Assistant ID not set. Create or load an assistant first.")
            sys.exit()
        data = self.client.beta.assistants.retrieve(self.id)
        try:
            config = data.model_dump() if hasattr(data, "model_dump") else dict(data)
            logger.info("Configuracion del asistente cargada con exito.")
            return config
        except Exception as e:
            logger.error("No se pudo cargar la configuracion del asistente.", exc_info= e)
            return None
        

class AssistantManager:
    """Manejar el conjunto de asistentes en una cuenta."""
    def __init__(self, client: OpenAI):
        self.client = client

    def list_assistants(self):
        response = self.client.beta.assistants.list()
        logger.info("Se cargaron %s asistentes del cliente.", len(response.data))
        return {
            a.id : {"name": a.name, "model": a.model, "created_at" : datetime.datetime.fromtimestamp(a.created_at).strftime("%Y/%m/%d-%H:%M:%S")}
            for a in response.data
        }

    def delete_assistant(self, assistant_id: str):
        self.client.beta.assistants.delete(assistant_id)
        logger.info("Assistant %s deleted.", assistant_id)