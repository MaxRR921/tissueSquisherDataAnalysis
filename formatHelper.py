def formatMoveTiming(timing):
    """GUI 'last move' label text."""
    if timing is None:
        return "last move: did not move"
    readings = f"{timing.readingWindow:.2f} s first→last reading"
    if timing.movingTime is None:
        return f"last move: no motion detected ({readings})"
    return f"last move: {timing.movingTime:.2f} s moving ({readings})"


def formatMoveLogLine(timestamp, startPos, move, endPos, timing):
    """One moves.md line: timestamp, move, speed, time, distance, velocity."""
    distance = abs(endPos - startPos)
    if timing is not None and timing.movingTime is not None:
        timeStr = f"{timing.movingTime:.3f} s"
        velocity = timing.velocity(distance)
        velocityStr = f"{velocity:.4f} mm/s" if velocity is not None else "n/a"
    else:
        timeStr = "no motion detected"
        velocityStr = "n/a"
    return (f"{timestamp} | move: {startPos:.3f} -> {move.targetHeight} | "
            f"speed set: {move.velocity} | time: {timeStr} | distance: {distance:.3f} mm | "
            f"velocity: {velocityStr}  \n")
