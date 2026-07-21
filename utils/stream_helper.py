"""
Stream Helper.

Implements ProgressBytesIO to wrap binary file buffers and report reading progress.
"""

import io


class ProgressBytesIO(io.IOBase):
    """
    A file-like object wrapper using a delegation pattern.
    Inheriting from io.IOBase forces C extensions (like Pandas) to invoke 
    Python methods, enabling progress tracking.
    """

    def __init__(self, initial_bytes: bytes, progress_callback=None):
        self._buffer = io.BytesIO(initial_bytes)
        self.total_size = len(initial_bytes)
        self.bytes_read = 0
        self.progress_callback = progress_callback

    def read(self, size=-1):
        data = self._buffer.read(size)
        self.bytes_read += len(data)
        if self.progress_callback:
            self.progress_callback(self.bytes_read, self.total_size)
        return data

    def readline(self, size=-1):
        data = self._buffer.readline(size)
        self.bytes_read += len(data)
        if self.progress_callback:
            self.progress_callback(self.bytes_read, self.total_size)
        return data

    def readinto(self, b):
        res = self._buffer.readinto(b)
        if res is not None:
            self.bytes_read += res
            if self.progress_callback:
                self.progress_callback(self.bytes_read, self.total_size)
        return res

    def seek(self, offset, whence=io.SEEK_SET):
        res = self._buffer.seek(offset, whence)
        # Reset tracker if rewound to start
        if offset == 0 and whence == io.SEEK_SET:
            self.bytes_read = 0
        return res

    def tell(self):
        return self._buffer.tell()

    def readable(self):
        return True

    def seekable(self):
        return True

