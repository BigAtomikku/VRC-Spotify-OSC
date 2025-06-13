def lrc_to_dictionary(lrc):
    lines = lrc.strip().split('\n')
    lrc_dict = {}

    for line in lines:
        timestamp, lyric = line.split(']', 1)
        timestamp = timestamp[1:]
        lyric = lyric.strip()
        minutes, seconds = timestamp.split(':')
        total_ms = int(minutes) * 60 * 1000 + float(seconds) * 1000
        lrc_dict[int(total_ms)] = lyric

    return lrc_dict
