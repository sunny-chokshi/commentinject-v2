"""Install the CommentInject probe + detector into an installed garak package.

garak discovers plugins by listing the files in its own ``garak/probes`` and ``garak/detectors``
directories (and imports them as ``garak.<category>.<module>``), so an external plugin has to be
placed there. This script symlinks (default) or copies our two modules into the garak package
of the Python interpreter that runs it, so run it with the interpreter garak is installed in:

    python install_plugins.py            # symlink (edits here take effect immediately)
    python install_plugins.py --copy     # copy modules + data (for read-only checkouts)
    python install_plugins.py --uninstall
"""

import argparse
import shutil
from pathlib import Path

import garak

HERE = Path(__file__).resolve().parent / "commentinject_garak"
FILES = {
    HERE / "probes" / "commentinject.py": ("probes", "commentinject.py"),
    HERE / "detectors" / "commentinject.py": ("detectors", "commentinject.py"),
}
DATA = HERE / "data" / "commentinject_v2.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()
    pkg = Path(garak.__file__).resolve().parent
    targets = [(src, pkg / cat / name) for src, (cat, name) in FILES.items()]
    targets.append((DATA, pkg / "data" / DATA.name))
    for src, dst in targets:
        if dst.is_symlink() or dst.exists():
            if not (dst.is_symlink() or a.copy or a.uninstall):
                raise SystemExit(f"refusing to overwrite non-symlink {dst}; use --copy or --uninstall")
            dst.unlink()
            print("removed", dst)
        if a.uninstall:
            continue
        if src == DATA and not a.copy:
            continue  # symlinked probe finds the data next to its real path
        if a.copy:
            shutil.copy2(src, dst)
        else:
            dst.symlink_to(src)
        print("installed", dst, "->", src)


if __name__ == "__main__":
    main()
