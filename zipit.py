import falcon
import logging
import json
from wsgiref import simple_server

from rq import Queue
from redis import Redis
from service_utils import compress


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge(
                'Request body is too large', msg)

    return hook


class CompressResources:
    def __init__(self):
        self.logger = logging.getLogger('compress_it. ' + __name__)
        redis_conn = Redis()
        self.q = Queue('default', connection=redis_conn)

    @falcon.before(max_body(64 * 1024))
    def on_get(self, req, resp):
        resp.body = json.dumps({"message": "Compression service demo"})
        resp.content_type = "application/json"
        resp.set_header('X-Powered-By', 'jms')
        resp.status = falcon.HTTP_200

    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp):
        # parse json, call module compress and notify
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            data = json.loads(body.decode('utf-8'))

            # check security sample
            """
            token = req.get_header('X-Auth-Token')
            if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

                raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          href='http://docs.example.com/auth')

            if not self._token_is_valid(token, project):
                description = ('The provided auth token is not valid. '
                               'Please request a new token and try again.')

                raise falcon.HTTPUnauthorized('Authentication required',
                                              description,
                                              href='http://docs.example.com/auth',
                                              scheme='Token; UUID')

            def _token_is_valid(self, token, project):
                return True  # Suuuuuure it's valid...

            """

            case_id = data.get('id', None)
            file_list = data.get('files', None)
            bucket_name = data.get('bucket', None)
            base_name = data.get('base_name', None)

            if case_id is not None and file_list is not None and bucket_name is not None:
                self.q.enqueue(compress.process_data, case_id, file_list, bucket_name, base_name)
                # response ok, task received
                resp.body = json.dumps(
                    {"message": "Compression task started, App will be notified via Pubnub when the task is complete"})
                resp.status = falcon.HTTP_200
            else:
                raise falcon.HTTPBadRequest('Invalid Data',
                                            'Information required not available')

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')


# falcon.API instances are callable WSGI apps
app = falcon.API()

zip_it = CompressResources()

app.add_route('/compress', zip_it)

"""
if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
"""