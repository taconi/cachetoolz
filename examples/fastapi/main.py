from http import HTTPStatus

from fastapi import FastAPI
from fastapi.routing import APIRoute

from .controllers import (
    create_hero,
    delete_hero,
    read_hero,
    read_hero_filter,
    update_hero,
)
from .database import init_db
from .models import Hero

app = FastAPI(
    on_startup=[init_db],
    routes=[
        APIRoute(
            '/hero/create',
            create_hero,
            methods=['POST'],
            response_model=Hero,
            status_code=HTTPStatus.CREATED,
            tags=['Hero'],
        ),
        APIRoute(
            '/hero/read',
            read_hero,
            methods=['GET'],
            response_model=list[Hero],
            tags=['Hero'],
        ),
        APIRoute(
            '/hero/read',
            read_hero_filter,
            methods=['POST'],
            response_model=list[Hero],
            tags=['Hero'],
        ),
        APIRoute(
            '/hero/update/{_id}',
            update_hero,
            methods=['PATCH'],
            response_model=Hero,
            tags=['Hero'],
        ),
        APIRoute(
            '/hero/delete/{_id}',
            delete_hero,
            methods=['DELETE'],
            status_code=HTTPStatus.NO_CONTENT,
            tags=['Hero'],
        ),
    ],
)
