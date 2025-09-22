from .graphql_utils import GraphQLUtils
from .request_builder import RequestBuilder
from .socket_handler import WebSocketHandler


class CafeXAPI(RequestBuilder, WebSocketHandler,GraphQLUtils ):
    pass


__version__ = "0.0.38"
