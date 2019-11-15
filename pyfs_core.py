import json
import posixpath

__version__ = '1.0'


class FileSystem(object):
    def __init__(self, fsname):
        self.json_decoder = json.JSONDecoder()
        self.filename = "filesystem_{}.json".format(fsname)
        self.nullfs = {
            "meta": {'pyfs-version': __version__},
            "contents": {
                'name': fsname,
                'subdirs': [],
                'files': []
            }
        }
        if not posixpath.exists(self.filename):
            with open(self.filename, 'w+') as filesystem:
                filesystem.write(json.dumps(self.nullfs))
                self.fs = self.nullfs
        else:
            with open(self.filename) as fsdata:
                self.fs = self.json_decoder.decode(fsdata.read())

