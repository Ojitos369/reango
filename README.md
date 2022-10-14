# You can check it in the blog
[React con Django](https://ojitos369.com/blog/#/post/36e7a37b-a6a6-4263-b41a-a004a055939a)

## Automatizando la integracion de un build de react a django  

### Preparando todo  
Requisitos previos:  
* python y pip
* node, npm, react

### Creando Proyecto
vamos a ir a la carpeta donde queremos nuestro proyecto y corremos los siguientes comandos en consola  

```shell
mkdir myapp #myapp puede cambiarser por el nombre que se quiera
cd myapp
py3 -m venv venv
source venv/bin/activate
pip install django
django-admin startproject myapp .
mkdir front
python manage.py startapp commands
python manage.py startapp views
cd front
npx create-react-app .
npm run build
cd ..
```  

#### Para Este punto deberiamos tener la siguiente estructura  

<div class="mt-3 row justify-content-center"><img src="https://ojitos369.com/media/blogs/36e7a37b-a6a6-4263-b41a-a004a055939a/tree_1.png" alt="tree_1.png" style="" class="col-5">
<img src="https://ojitos369.com/media/blogs/36e7a37b-a6a6-4263-b41a-a004a055939a/tree_2.png" alt="tree_2.png" style="" class="col-5"></div>
<div class="mt-3 row justify-content-center"><img src="https://ojitos369.com/media/blogs/36e7a37b-a6a6-4263-b41a-a004a055939a/tree_3.png" alt="tree_3.png" style="" class="col-5"><img src="https://ojitos369.com/media/blogs/36e7a37b-a6a6-4263-b41a-a004a055939a/tree_4.png" alt="tree_4.png" style="" class="col-5"></div>

### Modificando `myapp/settings.py`
El archivo `myapp/settings.py` lo abrimos y se editaran las siguientes partes
> Nota: tres puntos (...) indican que lo demas sigue igual  

```python
# Parte de Imports
import os


# Parte de apps
INSTALLED_APPS = [
    ...
    
    'views.apps.ViewsConfig',
    'commands.apps.CommandsConfig',
]

# Parte de templates
TEMPLATES = [
    {
        ...
        'DIRS': [
            ...
            os.path.join(BASE_DIR, 'templates')
        ],
    },
]

# Parte de statics (Remplazar el existente)
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
```  

###  Haciendo el comando para manage  

En el archivo `commands/management/commands/migrate_view.py` copiamos el siguiente codigo  

```py
import os
import re
from inspect import currentframe

from django.core.management.base import BaseCommand

# from ojitos369.utils import printwln

from myapp.settings import BASE_DIR

def printwln(*args, **kwargs):
    cf = currentframe()
    line = cf.f_back.f_lineno
    print(f"{line}: ", *args, **kwargs)


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        
        parser.add_argument('-n', '--name', type=str, help='app name')
        parser.add_argument('-o', '--origin', type=str, help='react build app path')
        parser.add_argument('-s', '--static', type=str, help='django static path')
        parser.add_argument('-t', '--template', type=str, help='django templates path')
        parser.add_argument('-rl', '--rl_localhost', type=str, help='replace endpoint localhost with / default: true')
        
        

    def handle(self, *args, **options):
        pwd = os.getcwd()
        name = options['name'] if options['name'] else 'main'
        
        react_build = options['origin'] if options['origin'] else os.path.join(BASE_DIR, 'front', 'build')
        templates_dir = f"templates/{options['template']}" if options['template'] else os.path.join(BASE_DIR, 'templates')
        static_dir = f"static/{options['static']}" if options['static'] else 'static/'#os.path.join(BASE_DIR, 'static')
        replace_localhost = str(options['rl_localhost']) if str(options['rl_localhost']) != 'None' else 'T'
        replace_localhost = True if replace_localhost[0].lower() in ('y', 't', 's',) else False
        
        printwln(f'react_build: {react_build}')
        printwln(f'templates_dir: {templates_dir}')
        printwln(f'static_dir: {static_dir}')
        
        os.chdir(pwd)
        
        loader = "{% load static %}"
        
        # copy build to static main
        try:
            os.system(f'rm -rf {static_dir}/{name}/')
        except Exception as e:
            pass
        
        try:
            os.system(f'mkdir -p {static_dir}/{name}/')
        except Exception as e:
            pass
            
        try:
            os.system(f'cp -rf {react_build}/* {static_dir}/{name}')
            # printwln('copy build to static/main')
        except Exception as e:
            pass
            # printwln('error en')
            # printwln(str(e))
        
        # mv index.html to templates main
        
        try:
            os.system(f'mkdir -p {templates_dir}/{name}')
        except Exception as e:
            pass
        
        try:
            os.system(f'touch {templates_dir}/{name}/index.html')
            os.system(f'rm {templates_dir}/{name}/index.html')
            # printwln('reset templates/main/index.html')
        except Exception as e:
            os.system(f'rm {templates_dir}/{name}/index.html')
            # printwln('reset templates/main/index.html')

        try:
            os.system(f'cp {static_dir}/{name}/index.html {templates_dir}/{name}/')
            # printwln('move index.html to templates/main/index.html')
        except Exception as e:
            pass
            # printwln('error en')
            # printwln(str(e))

        # add loader to index.html
        html = open(f'{templates_dir}/{name}/index.html', 'r').read()
        # printwln(html)
        html = loader + html
        # printwln(html)

        # replace all script and link like 
        # <script src="./index.js"></script> -> <script src="{% static 'main/index.js' %}"></script>

        structure = '''((href|src)=")(?!http)(./)?(.+?..{2,5})(")'''
        for match in re.finditer(structure, html):
        #     print()
        #     print()
        #     printwln(match.group(0))
            changes = match.group(1)+"{% static '" + str(f"{options['static']}/" if options['static'] else '') +name+"/"+match.group(4) +"' %}"+match.group(5)
            # printwln(changes)
            html = html.replace(match.group(0), changes)
            # print()
            # print()
        
        open(f'{templates_dir}/{name}/index.html', 'w').write(html)
        
        # get js name
        files = os.listdir(f'{static_dir}/{name}/static/js')
        # printwln(files)
        file_name = ''
        js_files = []
        for file in files:
            if file.endswith('.js'):
                js_files.append(file)
        # printwln(file_name)
        
        for file_name in js_files:
                printwln(file_name)
                # open js file
                js = open(f'{static_dir}/{name}/static/js/{file_name}', 'r').read()
                
                structure = '''(\\w=)\\w.\\w\\+"(static/)'''
                for match in re.finditer(structure, js):
                    new_name = f'{match.group(1)}"/{static_dir}/{name}/{match.group(2)}'
                    new_name = new_name.replace('//', '/')
                    printwln(match.group(0))
                    printwln(new_name)
                    js = js.replace(match.group(0), new_name)
                open(f'{static_dir}/{name}/static/js/{file_name}', 'w').write(js)
        
        if replace_localhost:
            js = open(f'{static_dir}/{name}/static/js/{file_name}', 'r').read()
            structure = '''https?://localhost(:\\d+)?'''
            for match in re.finditer(structure, js):
                printwln(match.group(0))
                js = js.replace(match.group(0), '')
            
            open(f'{static_dir}/{name}/static/js/{file_name}', 'w').write(js)


        printwln('Done')

```  

### Editando views  

En `views/views.py` ponemos 

```py

from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'myapp/index.html')

```  

En `views/urls.py` ponemos 


```py

from django.urls import path

from .views import index

app_name = 'views'
urlpatterns = [
    path('', index, name='index'),
]

```

### Editando urls principal

En `myapp/urls.py` incluimos los urls de views

```py
from django.urls import path, include

urlpatterns = [
    path('', include('views.urls')),
]
```

### Ejecutando el comando  
Ahora podemos ejecutar el comando para migrar el build  

```sh
python manage.py migrate_view -n myapp
python manage.py runserver
```

Ahora podemos react corriendo como vista de django

<div class="mt-3 row justify-content-center"><img src="https://ojitos369.com/media/blogs/36e7a37b-a6a6-4263-b41a-a004a055939a/Screenshot from 2022-10-14 10-41-49.png" alt="Screenshot from 2022-10-14 10-41-49.png" style="" class="col-5"></div>
<div style="height: 100px;"></div>