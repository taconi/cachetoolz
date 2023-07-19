from http import HTTPStatus

from flask import Flask
from flask_pydantic_api import apidocs_views, pydantic_api

from .controllers import (
    create_hero,
    delete_hero,
    read_hero,
    read_hero_filter,
    update_hero,
)
from .database import init_db

app = Flask(__name__)
app.ensure_sync(init_db)()
app.register_blueprint(apidocs_views.blueprint, url_prefix='/docs')

app.add_url_rule(
    '/hero/create',
    'create_hero',
    pydantic_api(success_status_code=HTTPStatus.CREATED, tags=['Hero'])(
        create_hero
    ),
    methods=['POST'],
)
app.add_url_rule(
    '/hero/read',
    'read_hero',
    pydantic_api(tags=['Hero'])(read_hero),
    methods=['GET'],
)
app.add_url_rule(
    '/hero/read',
    'read_hero_filter',
    pydantic_api(tags=['Hero'])(read_hero_filter),
    methods=['POST'],
)
app.add_url_rule(
    '/hero/update/<uuid:_id>',
    'update_hero',
    pydantic_api(tags=['Hero'])(update_hero),
    methods=['PATCH'],
)
app.add_url_rule(
    '/hero/delete/<uuid:_id>',
    'delete_hero',
    pydantic_api(success_status_code=HTTPStatus.NO_CONTENT, tags=['Hero'])(
        delete_hero
    ),
    methods=['DELETE'],
)
