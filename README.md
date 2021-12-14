# TP Parseo y Generación de Código, Universidad Nacional de Quilmes 2021

Se utiliza [SLY](https://github.com/dabeaz/sly) para implementar el parser y lexer de la gramática pedida.

## Instrucciones

Este repositorio contiene los siguientes archivos

- `lexer.py`: lexer de Flecha
- `parser.py`: parser de Flecha
- `ast.py`: ast de Flecha
- `serializer.py`: serializador de Flecha
- `compiler.py`: compilador de Flecha a Mamarracho
- `env.py`: entorno de variables
- `instructions.py`: instrucciones de compilación
- `main.py`: parsea e imprime un ast del programa Flecha
- los scripts:
    - `test_parser.sh`, ejecuta el parser con un archivo de prueba dentro de la carpeta `tests_parser` y compara su salida
    - `test_all_parser.sh`, ejecuta el parser con todos los archivos de prueba de la carpeta `tests_parser`
    - `test_compiler.sh`, ejecuta el compilador con un archivo de prueba dentro de la carpeta `test_codegen_v2/test_codegen` y compara su salida
    - `test_all_compiler.sh`, ejecuta el compilador con todos los archivos de prueba de la carpeta `test_codegen_v2/test_codegen`

## Instalación

Se necesita instalar **SLY** y **Python 3.6 >=**, para esto vamos a instalar dos dependencias [**pyenv**](https://github.com/pyenv/pyenv) y [**pipenv**](https://pypi.org/project/pipenv/).
Una vez instalados, instalamos la versión python 3.7 de Python con pyenv
- `pyenv install 3.8`
Luego, en la raíz del repositorio generamos un entorno virtual utilizando la versión 3.8 de Python
- `pipenv --python 3.8`
Inicializamos el entorno virtual
- `pipenv shell`
Finalmente instalamos las dependencias
- `pipenv install`

## Pruebas

Se pueden utilizar los scripts generados para realizar las pruebas del parser, por ejemplo:
Probar todos los casos de prueba.
- `./test_all_parser.sh` o `./test_all_compiler.sh`

O, usando main.py
- `python -m src.main tests_parser/test00.input`

## Referencias
- Pyenv installer: https://github.com/pyenv/pyenv-installer
