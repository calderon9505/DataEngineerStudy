# The Zen of python
import this

# Documentacion de Python
# https://docs.python.org/es/3/
# https://www.python.org/dev/peps/pep-0008/  IMPORTANTE!!! leerlo!!!

# Virtual Enviroment
#Un módulo es codigo de otros programadores (librerias)(los import)
#entorno virtual: tener python aislado para un proyecto que tiene sus propios módulos,
#está pensado para funcionar únicamente con ese proyecto
#en un directorio específico se define un venv con una version particular de python (no la global)
"sudo apt install python3.8-venv"       # libreria para crear venv (necesaria en wsl)
"python3 -m venv venv"                  # creacion entorno (-m module). (se crea carpeta venv)
"python -m venv venv"                   # creacion de venv en windows
### REVISAR ESTA FORMA DE CREAR AMBIENTES python3.10 -m venv sample_app_venv
#en la carpeta bin está el comando que activa el venv (en windows es "Script")
"source venv/bin/activate"              # crear alias y llamar activate (linux)
".\venv\Scripts\activate"               # alias activate=.\venv\Scripts\activate (windows)
"deactivate"

# Package Installer for Python PIP
#correr todo esto con el venv activado
"pip freeze"                            #módulos que se tienen instalados (pip3)
"pip install pandas"                    #pandas incluye pandas, pytz, numpy, python_dateutil, six
"pip freeze > requirements.txt"         
"pip install -r requirements.txt"       #instala las dependencias específicas del proyecto
#PYENV es otro manejador de paquetes más complejo pero más completo
"pip show _paquete_"
"pip list"

# Anaconda
#software completo pensado para los cientificos de datos
#distribucion espacial de python que permite crear venv y hacer pip de manera grafica