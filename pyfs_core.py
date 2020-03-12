import json
from os import path as posixpath, urandom as rand
from base64 import b64decode, b64encode
from Cryptodome.Cipher import ChaCha20

__version__ = '2.1'


class FileSystem(object):
    def __init__(self, fsname, key):
        self.json_decoder = json.JSONDecoder()
        self.filename = "filesystem_{}.json".format(fsname)
        self.nullfs = {
            "meta": {'pyfs-version': __version__},
            "contents": {
                'name': '',
                'type': 'dir',
                'files': [
                ]
            }
        }
        self.key = key
        if not posixpath.exists(self.filename):
            with open(self.filename, 'w+') as filesystem:
                filesystem.write(json.dumps(self.nullfs))
                self.fs = self.nullfs
        else:
            with open(self.filename, 'r+') as filesystem:
                self.fs = self.json_decoder.decode(filesystem.read())

    def update_fs(self):
        with open(self.filename, 'w+') as filesystem:
            filesystem.write(json.dumps(self.fs))

    def exists(self, abspath):
        return self.is_file(abspath) or self.is_dir(abspath)

    def is_file(self, abspath):
        path = abspath.strip('/').split('/')
        contents = self.fs['contents']['files']
        for j in range(len(path)):
            for i in contents:
                if j == len(path) - 1:
                    return i['type'] == 'file' and path[j] == i['name']
                else:
                    if path[j] == i['name'] and i['type'] == 'dir':
                        contents = i['files']
                        break
        return False

    def is_dir(self, abspath):
        path = abspath.strip('/').split('/')
        contents = self.fs['contents']['files']
        for j in range(len(path)):
            for i in contents:
                if path[j] == i['name'] and i['type'] == 'dir':
                    if j == len(path) - 1:
                        return True
                    else:
                        contents = i['files']
                        break
        return False

    def mkdir(self, dirname, location):
        data = {
            'name': dirname,
            'type': 'dir',
            'files': []
        }
        if location == '/':
            root = self.fs['contents']['files']
            for i in root:
                if i['name'] == dirname:
                    return 1
            root.append(data)
            return 0
        path = location.strip('/').split('/')
        root = self.fs['contents']['files']
        for j in path:
            for i in root:
                if j == i['name'] and i['type'] == 'dir':
                    root = i['files']
                    break
            else:
                return 1
        for i in root:
            if i['name'] == dirname:
                return 1
        root.append(data)
        return 0

    def mkfile(self, filename, location):
        data = {
            'name': filename,
            'type': 'file',
            'nonce': b64encode(rand(12)),
            'contents': ''
        }
        if location == '/':
            root = self.fs['contents']['files']
            for i in root:
                if i['name'] == filename:
                    return 1
            root.append(data)
            return 0
        path = location.strip('/').split('/')
        root = self.fs['contents']['files']
        for j in path:
            for i in root:
                if j == i['name'] and i['type'] == 'dir':
                    root = i['files']
                    break
            else:
                return 1
        for i in root:
            if i['name'] == filename:
                return 1
        root.append(data)
        return 0

    def rm(self, file, location):
        root = self.fs['contents']['files']
        if location != '/':
            path = location.strip('/').split('/')
            for j in path:
                for i in root:
                    if j == i['name'] and i['type'] == 'dir':
                        root = i['files']
                        break
                else:
                    return 1
        for i in range(len(root)):
            if root[i]['name'] == file:
                del root[i]
                return 0
        else:
            return 1

    def ls(self, location):
        root = self.fs['contents']['files']
        if location != '/':
            path = location.strip('/').split('/')
            for j in path:
                for i in root:
                    if j == i['name'] and i['type'] == 'dir':
                        root = i['files']
                        break
                else:
                    return 1
        out = []
        for i in root:
            out.append({'name': i['name'], 'type': i['type']})
        return out

    def read_file(self, location, file):
        root = self.fs['contents']['files']
        if location != '/':
            path = location.strip('/').split('/')
            for j in path:
                for i in root:
                    if j == i['name'] and i['type'] == 'dir':
                        root = i['files']
                        break
                else:
                    return 1
        for i in root:
            if i['name'] == file:
                data = b64decode(i['contents'])
                cipher = ChaCha20.new(key=self.key[:32], nonce=b64decode(i['nonce']))
                return cipher.decrypt(data)
        else:
            return 1

    def write_file(self, location, file, data: bytes) -> int:
        root = self.fs['contents']['files']
        if location != '/':
            path = location.strip('/').split('/')
            for j in path:
                for i in root:
                    if j == i['name'] and i['type'] == 'dir':
                        root = i['files']
                        break
                else:
                    return 1
        for i in root:
            if i['name'] == file:
                cipher = ChaCha20.new(key=self.key[:32], nonce=b64decode(i['nonce']))
                i['contents'] = b64encode(cipher.encrypt(data)).decode()
                return 0
        else:
            return 1
