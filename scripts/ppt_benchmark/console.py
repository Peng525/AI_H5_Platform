"""Console output safe on Windows GBK terminals."""
from __future__ import annotations

import sys


def safe_print(*args, **kwargs) -> None:
    text = " ".join(str(a) for a in args)
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write(text.encode(enc, errors="replace") + b"\n")
        sys.stdout.flush()
