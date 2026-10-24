"""Future child process entry with Linux parent-death protection; inert when imported."""
import ctypes
import os
from pathlib import Path
import signal
import sys

def bind_parent(expected):
    # Per-process Linux setting, not a host/account/security configuration change.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Cannot establish parent-death signal')
    if os.getppid() != expected:
        raise RuntimeError('Controller already exited; do not execute child work')

def main():
    parent, mode, root, output = sys.argv[1:]
    bind_parent(int(parent))
    root, output = Path(root).resolve(), Path(output).resolve()
    bundle = Path(__file__).resolve().parent
    if mode == 'preflight':
        from preflight import main as preflight
        preflight(root, output)
    elif mode == 'inference':
        import random
        import runpy
        os.sched_setaffinity(0, {0})
        random.seed(20261024)
        import numpy as np
        np.random.seed(20261024)
        sys.path.insert(0, str(bundle))
        sys.argv = [str(bundle / 'guarded_recorder.py'), str(output / 'P1')]
        runpy.run_path(sys.argv[0], run_name='__main__')
    elif mode == 'analyze':
        from analyze_saved import analyze
        analyze(root, output)
    else:
        raise ValueError('Unknown child mode')

if __name__ == '__main__':
    main()
