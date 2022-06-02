from aiohttp import web

from app.endpoints.reg_admin import admin_register_view, admin_register


def setup(app: web.Application) -> None:
    # app.router.add_get('/administrator/reg-form', admin_register_view)
    app.router.add_post('/administrator/register', admin_register)