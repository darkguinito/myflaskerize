from typing import Callable, Dict

HEADER = """# DO NOT EDIT THIS FILE. It is generated by flaskerize and may be
# overwritten"""


def _generate(
    contents,
    output_name: str,
    filename: str = None,
    mode: str = "w",
    dry_run: bool = False,
) -> None:
    if dry_run:
        print(contents)
    else:
        if filename is None:
            filename = f'{output_name.replace(".py", "")}.py'
        with open(filename, mode) as fid:
            fid.write(contents)

    if filename:
        print(f"Successfully created {filename}")


def hello_world(args) -> None:
    print("Generating a hello_world app")

    CONTENTS = f"""{HEADER}

import os
from flask import Flask, send_from_directory

def create_app():
    app = Flask(__name__)

    # Serve React App
    @app.route('/')
    def serve():
        return 'Hello, Flaskerize!'
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

    """
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )
    print("Successfully created new app")


def app_from_dir(args) -> None:
    """
    Serve files using `send_from_directory`. Note this is less secure than
    from_static_files as anything within the directory can be served.
    """

    print("Generating an app from static site directory")

    # The routing for `send_from_directory` comes directly from https://stackoverflow.com/questions/44209978/serving-a-create-react-app-with-flask  # noqa
    CONTENTS = f"""{HEADER}

import os
from flask import Flask, send_from_directory


def create_app():
    app = Flask(__name__, static_folder='{args.source}')

    # Serve static site
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()

"""
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )
    print("Successfully created new app")


def blueprint(args):
    """
    Static site blueprint
    """

    print("Generating a blueprint from static site")

    # The routing for `send_from_directory` comes directly from https://stackoverflow.com/questions/44209978/serving-a-create-react-app-with-flask  # noqa
    CONTENTS = f"""{HEADER}

import os
from flask import Blueprint, send_from_directory

site = Blueprint('site', __name__, static_folder='{args.source}')

# Serve static site
@site.route('/')
def index():
    return send_from_directory(site.static_folder, 'index.html')

"""
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )
    print("Successfully created new blueprint")


def wsgi(args):
    from flaskerize.utils import split_file_factory

    filename, func = split_file_factory(args.source)
    filename = filename.replace(".py", "")

    CONTENTS = f"""{HEADER}

from {filename} import {func}
app = {func}()
    """
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )
    print("Successfully created new wsgi")


def namespace(args):
    """
    Generate a new Flask-RESTplus API Namespace
    """

    CONTENTS = f"""from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_accepts import accepts, responds
import marshmallow as ma

api = Namespace('{args.output_name}', description='All things {args.output_name}')


class {args.output_name.title()}:
    '''A super awesome {args.output_name}'''

    def __init__(self, id: int, a_float: float = 42.0, description: str = ''):
        self.id = id
        self.a_float = a_float
        self.description = description


class {args.output_name.title()}Schema(ma.Schema):
    id = ma.fields.Integer()
    a_float = ma.fields.Float()
    description = ma.fields.String(256)

    @ma.post_load
    def make(self, kwargs):
        return {args.output_name.title()}(**kwargs)


@api.route('/')
class {args.output_name.title()}Resource(Resource):
    @accepts(schema={args.output_name.title()}Schema, api=api)
    @responds(schema={args.output_name.title()}Schema)
    def post(self):
        return request.parsed_obj

    @accepts(dict(name='id', type=int, help='ID of the {args.output_name.title()}'), api=api)
    @responds(schema={args.output_name.title()}Schema)
    def get(self):
        return {args.output_name.title()}(id=request.parsed_args['id'])

    @accepts(schema={args.output_name.title()}Schema, api=api)
    @responds(schema={args.output_name.title()}Schema)
    def update(self, id, data):
        pass

    @accepts(dict(name='id', type=int, help='ID of the {args.output_name.title()}'), api=api)
    def delete(self, id):
        pass

"""
    print(args)
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )

    if not args.without_test:
        namespace_test(args)


def namespace_test(args):
    """
    Generate a new Flask-RESTplus API Namespace
    """

    CONTENTS = f"""import pytest

from app.test.fixtures import app, client
from .{args.output_name} import {args.output_name.title()}, {args.output_name.title()}Schema


@pytest.fixture
def schema():
    return {args.output_name.title()}Schema()


def test_schema_valid(schema):  # noqa
    assert schema


def test_post(app, client, schema):  # noqa
    with client:
        obj = {args.output_name.title()}(id=42)
        resp = client.post('{args.output_name}/', json=schema.dump(obj).data)
        rv = schema.load(resp.json).data
        assert obj.id == rv.id


def test_get(app, client, schema):  # noqa
    with client:
        resp = client.get('{args.output_name}/?id=42')
        rv = schema.load(resp.json).data
        assert rv
        assert rv.id == 42

"""
    print(args)
    _generate(
        CONTENTS,
        output_name=args.output_name
        and args.output_name.replace(".py", "") + "_test.py",
        filename=args.output_file and args.output_file.replace(".py", "") + "_test.py",
        dry_run=args.dry_run,
    )


def dockerfile(args):

    CONTENTS = f"""FROM python:3.7 as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
RUN pip install --install-option="--prefix=/install" gunicorn
RUN pip install --install-option="--prefix=/install" flask

FROM base
COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "--error-logfile", "-", "{args.source}"]

"""
    _generate(
        CONTENTS,
        output_name=args.output_name,
        filename=args.output_file,
        dry_run=args.dry_run,
    )
    print("Successfully created new Dockerfile")
    print(
        "Next, run `docker build -t my_app_image .` to build the docker image and "
        "then use `docker run my_app_image -p 127.0.0.1:80:8080` to launch"
    )


# Mapping of keywords to generation functions
a: Dict[str, Callable] = {
    "hello-world": hello_world,
    "hw": hello_world,
    "dockerfile": dockerfile,
    "wsgi": wsgi,
    "app_from_dir": app_from_dir,
    "blueprint": blueprint,
    "bp": blueprint,
    "namespace": namespace,
    "ns": namespace,
}
