from sanic import Sanic
from werkzeug.exceptions import HTTPException

from app.misc.log import log


def register_extensions(sanic_app: Sanic):
    from app import extensions

    extensions.cors.init_app(sanic_app)


def register_views(sanic_app: Sanic):
    from app.views import route

    handle_exception_func = sanic_app.handle_exception
    handle_user_exception_func = sanic_app.handle_user_exception
    # register_blueprint 시 defer되었던 함수들이 호출되며, flask-restful.Api._init_app()이 호출되는데
    # 해당 메소드가 app 객체의 에러 핸들러를 오버라이딩해서, 별도로 적용한 handler의 HTTPException 관련 로직이 동작하지 않음
    # 따라서 두 함수를 임시 저장해 두고, register_blueprint 이후 함수를 재할당하도록 함

    route(sanic_app)

    sanic_app.handle_exception = handle_exception_func
    sanic_app.handle_user_exception = handle_user_exception_func


def register_hooks(sanic_app: Sanic):
    from app.hooks.error import broad_exception_error_handler, http_exception_handler
    from app.hooks.request_context import after_request

    sanic_app.after_request(after_request)
    sanic_app.register_error_handler(HTTPException, http_exception_handler)
    sanic_app.register_error_handler(Exception, broad_exception_error_handler)


def create_app(*config_cls) -> Sanic:
    log(message='Sanic application initialized with {}'.format(', '.join([config.__name__ for config in config_cls])),
        keyword='INFO')
            
    sanic_app = Sanic(__name__)

    for config in config_cls:
        sanic_app.config.from_object(config)

    register_extensions(sanic_app)
    register_views(sanic_app)
    register_hooks(sanic_app)

    return sanic_app
