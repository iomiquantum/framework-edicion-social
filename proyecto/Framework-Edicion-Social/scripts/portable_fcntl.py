"""Small flock compatibility surface for this snapshot, never installed globally.

Windows serializes shared readers too. OS file descriptors release locks on close.
This is for local disks, not coordination across PCs/network shares.
"""
import os
import time

LOCK_SH, LOCK_EX, LOCK_NB, LOCK_UN = 1, 2, 4, 8


def flock(fd, operation):
    fd = fd if isinstance(fd, int) else fd.fileno()
    if os.name != 'nt':
        import fcntl
        return fcntl.flock(fd, operation)
    import errno
    import msvcrt
    position = os.lseek(fd, 0, os.SEEK_CUR)
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        if operation & LOCK_UN:
            return msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        if not operation & (LOCK_EX | LOCK_SH):
            raise ValueError('Unsupported lock operation')
        while True:
            try:
                return msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if operation & LOCK_NB:
                    raise BlockingIOError(error.errno, str(error)) from error
                time.sleep(0.1)
    finally:
        os.lseek(fd, position, os.SEEK_SET)
