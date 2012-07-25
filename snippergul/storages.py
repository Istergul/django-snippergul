import os
import hashlib
import errno
import random
import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_unicode

class HashPathStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, depth=2, dirname_len=2):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.base_url = base_url
        self.depth = depth
        self.dirname_len = dirname_len

    def save(self, name, content):
        # Get the content name if name is not given
        if name is None:
            name = content.name

        # Get the SHA1 hash of the uploaded file
        str4hash = unicode(datetime.datetime.today().isoformat()) + unicode(random.randint(1, 1000000)) + name
        str4hash = str4hash.encode('utf8')
        sha1sum = hashlib.sha1(str4hash).hexdigest()

        # Build the new path and split it into directory and filename
        if name:
            dir_list = [os.path.split(name)[0]]
            for p in range(self.depth):
                start = p * self.dirname_len
                end = start + self.dirname_len
                dir_list.append(sha1sum[start:end])
            dir_list.append(sha1sum)
            if dir_list[0] == u'/':
                dir_list.pop(0)
            name = os.path.join(*dir_list) + os.path.splitext(name)[1]
        dir_name, file_name = os.path.split(name)
        if dir_name[0] == '/':
            dir_name = dir_name[1:]

        # Return the name if the file is already there
        if os.path.exists(name):
            return name

        # Try to create the directory relative to the media root
        try:
            os.makedirs(os.path.join(self.location, dir_name))
        except OSError, e:
            if e.errno is not errno.EEXIST:
                raise e

        # Save the file
        if name[0] == '/':
            name = name[1:]
        name = self._save(name, content)

        # Store filenames with forward slashes, even on Windows
        return force_unicode(name.replace('\\', '/'))
