from flask import Flask, render_template, request, send_file
from livereload import Server
import src.params as params
import argparse
from src.cli_args_manager import CLIArgsManager

import src.main
import io
import zipfile

app = Flask(__name__)

def get_args_from_parser(parser: argparse.ArgumentParser) -> dict[str, dict[str, str]]:

    spec = {}

    for action in parser._actions:
        if action.dest == 'help':
            continue

        field = {
            'default': action.default,
            'name': action.dest.replace('_', '-'),
            'hover': action.help
        }

        if action.choices:
            field['type'] = 'select'
            field['opts'] = action.choices

        elif isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction):
            field['type'] = 'checkbox'

        else:
            if action.default is not None and action.dest != 'spacing' and action.dest != 'bleed':
                field['type'] = 'range'

        spec[action.dest] = field
    return spec


def extract_args_from_page(page_kwargs: dict) -> list[str]:
    args = []
    form = request.form

    for kwarg in page_kwargs:
        kwarg = kwarg.replace('_', '-')
        args.append(f'--{kwarg}')
        form_value = form.get(kwarg)

        if '-x' in kwarg or '-y' in kwarg:
            if form.get(f'separate-{kwarg[:-2]}') is None:
                args.pop()
                continue

        if form_value == 'True':
            continue

        if form_value is None:
            args.pop()
            continue

        args.append(f'{form_value}')

    return args


@app.route('/', methods=['GET', 'POST'])
def index():
    args = CLIArgsManager(argv=[]).create_cli_args()
    page_kwargs = get_args_from_parser(args)

    if request.method == 'POST':

        args = extract_args_from_page(page_kwargs)
        xml = request.files['uploaded_xml']

        src.main.main(xml, argv=args) 

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            for file in params.PAGE_PATH.iterdir():
                with open(file, 'rb') as f:
                    z.writestr(file.name, f.read())
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name='Pages.zip',
            mimetype='application/zip'
        )
    
    return render_template('index.html', page_kwargs=page_kwargs)


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.watch('frontend/templates/')
    server.watch('frontend/static/')
    server.serve(port=5000, debug=True)
    
