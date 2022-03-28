def parse_flines(file):
    with open(file) as f:
        idx_lines = [int(l[:2]) for l in f if l[:2] != "\n"]
        f.seek(0)
        lines = [{"idx": int(l[:2]), "value": l[3:-1]} for l in f if l[:2] != "\n"]

    return idx_lines, lines
