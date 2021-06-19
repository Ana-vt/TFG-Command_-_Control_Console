# TFG-Consola-cibersituacional
Este proyecto se basa en el desarrollo de una consola de mando y control del proyecto PLICA, capaz de administrar usuarios, gestionar los distintos sensores y subsistemas deplegados y visualizar el riesgo dinámico.
## Instalación :wrench:
Para instalar y ejecutar correctamente el proyecto se deben seguir los siguientes pasos:
1. Tener instalado Git.
2. Instalar **MySQLWorkbench** a través de https://dev.mysql.com/downloads/
  - 2.1 Se debe seleccionar "Servidor de comunidad Mysql"
  - 2.2 A continuación "Go to download page"
  - 2.3 Descargar vía web (ocupa menos)
  - 2.4 Ejecutar el fichero descargado
  - 2.5 Seleccionar developer default
  - 2.6 A continuación pulsar NEXT ( no seleccionar descarga de manual, no es necesario)
  - 2.7 Finalmente pulsar EXECUTE y esperar a que termine la ejecución. Cuando esta finalice se debe ingresar un usuario y contraseña
3. Utilizar un editor de código, se recomienda **Visual Studio Code** :bangbang:
4. Clonar el repositorio con el comando *git clone* https://github.com/Ana-vt/TFG-Consola-cibersituacional.git
5. Abrir el terminal de Visual Studio y ejecutar ***pip install -r requirements.txt***
6. Ejecutar ***pip install virtualenv env***. A continucación ***virtualenv env*** y ***.\env\Scripts\activate***
  - Si tu equipo no permite ejecutar scripts, en el caso de windows, acceder al PowerShell como administrador y ejecutar ***Set_ExecutionPolicy Unrestricted*** y volver a ejecutar el paso :six:
7. Ejecutar ***pip install Flask***. Seguidamente ***pip install flask-mysql***
9. Ejecutar ***pip install bcrypt***
10.Por útlimo ejecutar ***pip install Crypto*** y ***pip install pycryptodome*** e ir a la carpeta **/env**, una vez ahí acceder a **Lib\site-packages** y cambiar el módulo **crypto** por **Crypto** :bangbang:
11. Finalmente ejecutar ***pip install Paramiko*** y correr el programa con ***python run.py*** :+1:
Al abrir el navegador se debe ver lo siguiente. (Ingresar *admin* y *soyadmin*)
<img src="/acceso.PNG" alt="Imagen inicio de sesión"/>
