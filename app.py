"""Entry point utama 2EZ4U APP:  python app.py
"""

import os
import subprocess
import sys

AKAR = os.path.dirname(os.path.abspath(__file__))


def lepas_dari_terminal():
    """True bila aplikasi sudah dibuka ulang via pythonw.exe di proses terpisah."""
    if os.name != "nt" or sys.executable.lower().endswith("pythonw.exe"):
        return False
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        return False
    subprocess.Popen([pythonw, os.path.join(AKAR, "app.py")], cwd=AKAR, close_fds=True,
                     creationflags=subprocess.DETACHED_PROCESS
                     | subprocess.CREATE_NEW_PROCESS_GROUP)
    return True


if __name__ == "__main__" and not lepas_dari_terminal():
    sys.path.insert(0, AKAR)
    from frontend.ui import jalankan
    jalankan()