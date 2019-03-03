from pathlib import Path
from pprint import pprint
import keyword
import builtins
import textwrap
# def is_module(str):
#     for line in str.split('\n'):
#         if line.startswith('class '):
'''
list modules and singletons
list classes in base folder

prefabs     # all classes
scripts

models
    procedural

fonts
textures


samples
tutorials
'''




def indentation(line):
    return len(line) - len(line.lstrip())


def get_module_attributes(str):
    attrs = list()

    for l in str.split('\n'):
        if len(l) == 0:
            continue
        if l.startswith(tuple(keyword.kwlist) + tuple(dir(builtins)) + (' ', '#', '\'', '\"', '_')):
            continue
        attrs.append(l)

    return attrs


def get_classes(str):
    classes = dict()
    for c in str.split('\nclass ')[1:]:
        class_name = c.split(':', 1)[0]
        if class_name.startswith(('\'', '"')):
            continue
        # print(class_name)
        classes[class_name] = c.split(':', 1)[1]

    return classes


def get_class_attributes(str):
    attributes = list()
    lines = str.split('\n')
    start = 0
    end = len(lines)
    for i, line in enumerate(lines):
        found_init = False
        # end = i
        if line.strip().startswith('def __init__'):
            if found_init:
                break

            start = i
            for j in range(i+1, len(lines)):
                if (indentation(lines[j]) == indentation(line)
                and not lines[j].strip().startswith('def late_init')
                ):
                    end = j
                    found_init = True
                    break


    init_section = lines[start:end]
    # print('init_section:', start, end, init_section)

    for i, line in enumerate(init_section):
        if line.strip().startswith('self.') and ' = ' in line:
            stripped_line = line.split('self.', 1)[1]
            if '.' in stripped_line.split(' ')[0] or stripped_line.startswith('_'):
                continue

            key = stripped_line.split(' = ')[0]
            value = stripped_line.split(' = ')[1]

            if i < len(init_section) and indentation(init_section[i+1]) > indentation(line):
                # value = 'multiline'
                start = i
                end = i
                indent = indentation(line)
                for j in range(i+1, len(init_section)):
                    if indentation(init_section[j]) <= indent:
                        end = j
                        break

                for l in init_section[start+1:end]:
                    value += '\n' + l[4:]

            attributes.append(key + ' = ' + value)


    if '@property' in code:
        # attributes.append('properties:\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('@property'):
                name = lines[i+1].split('def ')[1].split('(')[0]
                if not name in [e.split(' = ')[0] for e in attributes]:
                    attributes.append(name)

    return attributes


def get_functions(str, is_class=False):
    functions = dict()
    lines = str.split('\n')

    functions = list()
    lines = str.split('\n')
    for i, line in enumerate(lines):

        if line.strip().startswith('def '):
            if not is_class and line.split('(')[1].startswith('self'):
                continue

            name = line.split('def ')[1].split('(')[0]
            if name.startswith('_') or lines[i-1].strip().startswith('@'):
                continue

            params = line.replace('(self, ', '(')
            params = params.replace('(self)', '()')
            params = params.split('(')[1].split(')')[0]

            comment = ''
            if '#' in line:
                comment = '#' + line.split('#')[1]

            functions.append((name, params, comment))

    return functions


def get_example(str):
    key = '''if __name__ == '__main__':'''
    # if not key in str:
    #     return ''
    lines = list()
    example_started = False
    for l in str.split('\n'):
        if example_started:
            lines.append(l)

        if l == key:
            example_started = True

    example = '\n'.join(lines)
    example = textwrap.dedent(example)
    ignore = ('app = Ursina()', 'app.run()', 'from ursina import *')
    if 'class Ursina' in str:
        ignore = ()

    lines = [e for e in example.split('\n') if not e in ignore and not e.startswith('#')]
    example = '\n'.join(lines)
    return example.strip()


def is_singleton(str):
    for l in str.split('\n'):
        if l.startswith('sys.modules['):
            return True

    result = False


path = Path('.') / 'ursina'

init_file = ''
with open(Path('./ursina/__init__.py')) as f:
    init_file = f.read()

# print(init_file)
module_info = dict()
class_info = dict()

for f in path.glob('*.py'):
    if '__' in str(f):
        continue

    with open(f) as t:
        code = t.read()

        if not is_singleton(code):
            name = f.name.split('.')[0]
            attrs, funcs = list(), list()
            attrs = get_module_attributes(code)
            funcs = get_functions(code)
            example = get_example(code)
            if attrs or funcs:
                module_info[name] = ('', attrs, funcs, example)

            # continue
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                # print(class_name)
                if 'def __init__' in class_definition:
                    # init line
                    params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code)

                class_info[class_name] = (params, attrs, methods, example)
        # singletons
        else:
            module_name = f.name.split('.')[0]
            classes = get_classes(code)
            for class_name, class_definition in classes.items():
                # print(module_name)
                attrs, funcs = list(), list()
                attrs = get_class_attributes(class_definition)
                methods = get_functions(class_definition, is_class=True)
                example = get_example(code)

                module_info[module_name] = ('', attrs, funcs, example)


prefab_info = dict()
for f in path.glob('internal_prefabs/*.py'):
    if '__' in str(f):
        continue

    # if f.is_file() and f.name.endswith(('.py', )):
    with open(f) as t:
        code = t.read()
        classes = get_classes(code)
        for class_name, class_definition in classes.items():
            if 'def __init__' in class_definition:
                params =  '__init__('+ class_definition.split('def __init__(')[1].split('\n')[0][:-1]
            attrs = get_class_attributes(class_definition)
            methods = get_functions(class_definition, is_class=True)
            example = get_example(code)

            prefab_info[class_name] = (params, attrs, methods, example)


style = '''
    <style>
        html {
          scrollbar-face-color: #646464;
          scrollbar-base-color: #646464;
          scrollbar-3dlight-color: #646464;
          scrollbar-highlight-color: #646464;
          scrollbar-track-color: #000;
          scrollbar-arrow-color: #000;
          scrollbar-shadow-color: #646464;
          scrollbar-dark-shadow-color: #646464;
        }

        ::-webkit-scrollbar { width: 8px; height: 3px;}
        ::-webkit-scrollbar-button {  background-color: #222; }
        ::-webkit-scrollbar-track {  background-color: #646464;}
        ::-webkit-scrollbar-track-piece { background-color: #111;}
        ::-webkit-scrollbar-thumb { height: 50px; background-color: #222; border-radius: 3px;}
        ::-webkit-scrollbar-corner { background-color: #646464;}}
        ::-webkit-resizer { background-color: #666;}
    </style>

    <body style="
        margin: auto;
        background-color: hsl(0, 0%, 10%);
        color: hsl(0, 0%, 80%);
        font-family: monospace;
        position: absolute;
        top:0;
        left: 24em;
        font-size: 1.25em;
        font-weight: lighter;>
    '''
html = ''
sidebar = '''<pre><div style="
    left: 0px;
    position: fixed;
    top: 0px;
    padding-top:40px;
    padding-left:20px;
    bottom: 0;
    overflow-y: scroll;
    width: 15em;
    background-color: hsl(0, 0%, 10%);
    color: hsl(0, 0%, 80%);
    # overflow: hidden;
    ">'''


for i, class_dictionary in enumerate((module_info, class_info, prefab_info)):
    for name, attrs_and_functions in class_dictionary.items():
        params, attrs, funcs, example = attrs_and_functions[0], attrs_and_functions[1], attrs_and_functions[2], attrs_and_functions[3]

        params = params.replace('__init__', name.split('(')[0])
        params = params.replace('(self, ', '(')
        params = params.replace('(self)', '()')

        name = name.replace('ShowBase', '')
        name = name.replace('NodePath', '')
        for parent_class in ('Entity', 'Button', 'Text', 'Collider'):
            name = name.replace(f'({parent_class})', f'(<a style="color: gray ;" href="#{parent_class}">{parent_class}</a>)')

        base_name = name
        if '(' in base_name:
            base_name = base_name.split('(')[0]
            base_name = base_name.split(')')[0]
        name = name.replace('(', '<font color="gray">(')
        name = name.replace(')', ')</font>')

        color = f'color: hsl({90-(i*30)}, 70%, 50%)'
            # color = ('color: hsl(140, 70%, 50%)')

        sidebar += f'''<a style="{color}" href="#{base_name}">{base_name}</a>\n'''
        html += '\n'
        html += f'''<div id="{base_name}"><div id="header" style="{color}; font-size:1.5em;">{name}</div>'''
        html += '<pre style="position:relative; padding:0em 0em 2em 1em; margin:0;">'
        if params:
            params = f'<params id="params" style="color: white;">{params}</params>\n'
            html += params + '\n'

        for e in attrs:
            if ' = ' in e:
                e = f'''{e.split(' = ')[0]}<font color="gray"> = {e.split(' = ')[1]}</font> '''

            html += f'''{e}\n'''

        html += '\n'
        for e in funcs:
            e = f'{e[0]}(<font color="gray">{e[1]}</font>)   <font color="gray">{e[2]}</font>'
            html += e + '\n'

        if example:
            html += '\n<div id="example" style="font-color: red; padding-left: 1em; background-color: hsl(0, 0%, 15%);">' + example +'\n</div>'


        html += '\n</pre></div>'

# print(html)
sidebar += '</div>'
html += '</div>'
html = sidebar + style + html + '</body>'
with open('documentation.html', 'w') as f:
    f.write(html)