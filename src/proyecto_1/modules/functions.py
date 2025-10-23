import os
import shutil
import sys
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from proyecto_1.modules.loggers import logger

def run_git(*args, where:str) -> list[str]:
    logger.info(f'Ejecuando: {" ".join([i for i in args if ":github_pat_" not in i])}')
    result = subprocess.run([*args], 
                                cwd= where, 
                                capture_output= True, 
                                text= True, 
                                timeout=30)
    return result

def git_init(repo_dir:str):
    git_folder = repo_dir / ".git"
    if not git_folder.exists():
        logger.info(f"No existe .git en el directorio {os.path.basename(repo_dir)}. Creandolo...")
        out = run_git("git","init", where= repo_dir)
        if out.returncode == 0:
            logger.info(f"Repositorio iniciado en {repo_dir}")
        else:
            logger.error(f"No se pudo iniciar git en {repo_dir}. Ver error:", exc_info= out.stderr.lower())
    else:
        logger.info(f"Ya existe el repositorio .git en {repo_dir}")
        
def git_add_remote(repo_dir: str, remote_url: str, remote_name="origin"):
    """Agrega un remoto al repositorio, si no existe ya."""

    # Verificar si el remoto ya existe
    out = run_git("git", "remote", "-v", where=repo_dir)
    if remote_name in out.stdout:
        logger.info(f"El remoto '{remote_name}' ya existe en la configuración.")
        return out

    # Agregar el remoto
    out = run_git("git", "remote", "add", remote_name, remote_url, where= repo_dir)
    if out.returncode == 0:
        logger.info(f"Remoto agregado: {remote_name} -> {remote_url if not "github_pat" in remote_url else "url oculto por seguridad."}")
        return out
    elif "not a git repository" in out.stderr:
        logger.error("Debe ejecutar primero 'git init' antes de agregar un remoto.")
        sys.exit()
    else:
        logger.error(f"Error al agregar el remoto '{remote_name}'.", exc_info=out.stderr)
        sys.exit()
        return False

def git_set_branch(repo_dir: str, branch = "main"):
    out = run_git("git", "branch", "-M", branch, where= repo_dir)
    return out

def set_upstream(repo_dir, branch = "main"):
    run_git("git", "push", "-u", "origin", branch, where= repo_dir)

def config_git(repo_dir:str, repo_url:str, branch= "main"):
    # internet_conn
    git_init(repo_dir= repo_dir)
    git_add_remote(repo_dir, repo_url)
    git_set_branch(repo_dir)
    return True

def git_commit_and_push(repo_dir: Path, file_path: Path, message= " ", branch="main"):
    """Hace commit y push de un archivo cuando hay cambios."""
    commit_message = f"{message} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    try:
        out = run_git("git", "status", "--porcelain", str(file_path), where= repo_dir)
        print(out.stdout)
        if out.stdout.strip() == "":
            logger.info("No hay cambios en %s, no se hace commit.", file_path)
            return False

        run_git("git", "add", str(file_path), where=repo_dir)
        logger.info("Archivo agregado: %s", file_path)

        run_git("git", "commit", "-m", commit_message, where=repo_dir)
        logger.info("Commit realizado: %s", commit_message)

        try:
            run_git("git", "push", "-u", "origin", branch, where=repo_dir)
            logger.info("Push realizado a rama %s", branch)

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.lower() if e.stderr else ""
            if "fetch first" in stderr or "rejected" in stderr:
                logger.warning("Conflicto detectado. Ejecutando pull --rebase.")
                subprocess.run(["git", "pull", "origin", branch, "--rebase"], cwd=repo_dir, check=True)
                subprocess.run(["git", "push", "origin", branch], cwd=repo_dir, check=True)
            else:
                logger.error("Error al hacer push.", exc_info=e)
                return False

        return True

    except Exception as e:
        logger.error("Error general durante commit/push.", exc_info=e)
        return False

def temp_file(config_path:str, md_path:str, content:dict):
   
    with open(config_path, mode= "w", encoding= "utf-8") as config_file:
        text = json.dumps(content, indent= 4, ensure_ascii= False)
        config_file.write(text)
        logger.info(f"Config de asistente escrita.")
    with open(md_path, mode= "w", encoding= "utf-8") as md_file:
        text = json.dumps(content, indent= 4, ensure_ascii= False)
        prompt = content["instructions"] if content["instructions"] else ""
        md_file.write(prompt)
        logger.info(f"Prompt de asistente escrito.")

def delete_temp_file(path:str):
    files = [item.name for item in path.iterdir()]
    for file in files:
        file_path = path / file
        shutil.rmtree(file_path)
        logger.info("Directorios temporales eliminados.")

def verify_env_vars(env_vars: dict):
    for env_var, value in env_vars.items():
        if value == None:
            logger.error(f"No se a configurado {env_var} en el archivo .env (variables de entorno). Finalizando ejecucion.")
            sys.exit()
            return False
    logger.info(f"Variables de entorno {str(list(env_vars.keys())).lstrip("[").rstrip("]")}encontradas y cargadas.")
    return True

# def internet_conn():
#     try:
#         a = requests.get("https://www.google.com")
#         return a
#     except requests.ConnectionError as err:
#         logger.error("No hay conexion a internet. Verifique su conexion.")
#         sys.exit()
#         return err
        