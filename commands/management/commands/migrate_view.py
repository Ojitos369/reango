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