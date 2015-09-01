import falcon
import logging
import json
from wsgiref import simple_server

__author__ = 'jms'


# import uuid
# import requests


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class JSONTranslator(object):
    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])


class CompressResources:
    def __init__(self):
        self.logger = logging.getLogger('compress_it. ' + __name__)

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        resp.body = '{"message": "Compression service demo"}'
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp):
        # parse json, call module compress and notify

        # response ok, task received
        resp.body = '{"message": "Compression started, app will be notified via Pubnub when the task is complete"}'
        resp.status = falcon.HTTP_200
        pass


# falcon.API instances are callable WSGI apps
app = falcon.API()

zip_it = CompressResources()

app.add_route('/compress', zip_it)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
