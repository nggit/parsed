import unittest
import json

from parsed import ParseHeader

def decode_dict(data, encoding='latin-1'):
    if isinstance(data, dict):
        return {key.decode(encoding): decode_dict(value, encoding) for key, value in data.items()}
    elif isinstance(data, list):
        return [decode_dict(item, encoding) for item in data]
    elif type(data) in (bytearray, bytes):
        return data.decode(encoding)
    else:
        return data

class TestParseHeader(unittest.TestCase):
    tests_run = 0

    def setUp(self):
        self.__class__.tests_run += 1
        self.obj = ParseHeader()

    def tearDown(self):
        print('\r\033[2K{0:d}. {1:s}'.format(self.__class__.tests_run, self.id().split('.')[-1]))
        print(json.dumps(decode_dict(self.obj.getheaders()), sort_keys=True, indent=4))

    def test_empty(self):
        self.obj.parse(b'')
        self.assertFalse(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), None)
        self.assertEqual(self.obj.getmethod(), None)
        self.assertEqual(self.obj.getpath(), None)
        self.assertEqual(self.obj.getversion(), None)
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)
        self.assertEqual(self.obj.save(), b'')

    def test_break(self):
        self.obj.parse(b'\r\n\r\n')
        self.assertFalse(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), None)
        self.assertEqual(self.obj.getmethod(), None)
        self.assertEqual(self.obj.getpath(), None)
        self.assertEqual(self.obj.getversion(), None)
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)
        self.assertEqual(self.obj.save(), b'\r\n\r\n')

    def test_request_no_host_10(self):
        self.obj.parse(b'GET / HTTP/1.0\r\n\r\n')
        self.assertTrue(self.obj.is_request)
        self.assertTrue(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), None)
        self.assertEqual(self.obj.getmethod(), b'GET')
        self.assertEqual(self.obj.getpath(), b'/')
        self.assertEqual(self.obj.getversion(), b'1.0')
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)

    def test_request_no_host_11(self):
        self.obj.parse(b'GET / HTTP/1.1\r\nAccept: text/html\r\nAccept: image/*\r\n\r\n')
        self.assertTrue(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), b'')
        self.assertEqual(self.obj.getmethod(), b'GET')
        self.assertEqual(self.obj.getpath(), b'/')
        self.assertEqual(self.obj.getversion(), b'1.1')
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)

    def test_request_bad(self):
        self.obj.parse(b' HTTP/1.1\r\nHost: example.com:443\r\n\r\n')
        self.assertFalse(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), b'example.com:443')
        self.assertEqual(self.obj.getmethod(), None)
        self.assertEqual(self.obj.getpath(), None)
        self.assertEqual(self.obj.getversion(), None)
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)

    def test_request_bad_head(self):
        self.obj.parse(b'HEAD HTTP/1.1\r\nHost: example.com:443\r\n\r\n')
        self.assertTrue(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), b'example.com:443')
        self.assertEqual(self.obj.getmethod(), b'')
        self.assertEqual(self.obj.getpath(), b'')
        self.assertEqual(self.obj.getversion(), b'')
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)

    def test_request_bad_path(self):
        self.obj.parse(b'HEAD /path to/dir HTTP/1.1\r\nHost: example.com:443\r\n\r\n')
        self.assertTrue(self.obj.is_request)
        self.assertTrue(self.obj.is_valid_request)
        self.assertFalse(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), b'example.com:443')
        self.assertEqual(self.obj.getmethod(), b'HEAD')
        self.assertEqual(self.obj.getpath(), b'/path to/dir')
        self.assertEqual(self.obj.getversion(), b'1.1')
        self.assertEqual(self.obj.getstatus(), None)
        self.assertEqual(self.obj.getmessage(), None)

    def test_response(self):
        self.obj.parse(b'HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n200 OK\r\n')
        self.assertFalse(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertTrue(self.obj.is_response)
        self.assertTrue(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), None)
        self.assertEqual(self.obj.getmethod(), None)
        self.assertEqual(self.obj.getpath(), None)
        self.assertEqual(self.obj.getversion(), b'1.0')
        self.assertEqual(self.obj.getstatus(), 200)
        self.assertEqual(self.obj.getmessage(), b'OK')

    def test_response_bad_status(self):
        self.obj.parse(b'HTTP/1.0 xxx Not Found\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n404 Not Found\r\n')
        self.assertFalse(self.obj.is_request)
        self.assertFalse(self.obj.is_valid_request)
        self.assertTrue(self.obj.is_response)
        self.assertFalse(self.obj.is_valid_response)
        self.assertEqual(self.obj.gethost(), None)
        self.assertEqual(self.obj.getmethod(), None)
        self.assertEqual(self.obj.getpath(), None)
        self.assertEqual(self.obj.getversion(), b'')
        self.assertEqual(self.obj.getstatus(), 0)
        self.assertEqual(self.obj.getmessage(), b'')

    def test_response_excludes_remove_append_save(self):
        self.obj.parse(b'HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n404 Not Found\r\n', [b'connection'])
        self.assertEqual(self.obj.save(), b'HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found\r\n')
        self.assertEqual(self.obj._header.get(b'content-type'), [b'Content-Type: text/plain'])
        self.obj.remove([b'content-type'])
        self.assertEqual(self.obj._header.get(b'content-type'), None)
        self.obj.append({b'Content-Type': b'text/html'})
        self.assertEqual(self.obj._header.get(b'content-type'), [b'Content-Type: text/html'])
        self.assertEqual(self.obj.save(), b'HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n404 Not Found\r\n')

if __name__ == '__main__':
    unittest.main()
