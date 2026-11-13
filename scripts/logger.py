import time

import formatHelper


def logMove(move, startPos, endPos, timing, path="moves.md"):
    """Append one line per executed move to moves.md. Time is first→last detected position change
    (same as the GUI's 'last move' label)."""
    line = formatHelper.formatMoveLogLine(time.strftime('%Y-%m-%d %H:%M:%S'), startPos, move, endPos, timing)
    try:
        with open(path, mode="a", encoding="utf-8") as f:
            f.write(line)
    except OSError as e:
        print(f"[Warning] Could not write {path}: {e}")
