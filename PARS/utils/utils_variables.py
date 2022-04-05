from datetime import datetime


def find_sub_list(sl, l):
    sll = len(sl)
    return [
        ind
        for ind in (i for i, e in enumerate(l) if e == sl[0])
        if l[ind : ind + sll] == sl
    ]


def distance(len_my_list, idx_1, idx_2):
    return (idx_2 - idx_1) % len_my_list


def parse_ri(x):
    return float(x)


def parse_z(x):
    return float(x)


def parse_sample_interval(x):
    return int(x)


def parse_serial(x):
    return int(x)


def parse_datetime(x):
    return datetime.strptime(x, "%d.%m.%Y %H:%M:%S")


def parse_erro(x):
    return int(x)


def parse_vpd(x, mask, flag):
    vpd = [
        [int(y) for y in x[i : i + (32 * 4)].split(";")[:-1]]
        for i in range(0, len(x), (32 * 4))
    ]
    if flag:
        return [
            [i * j for i, j in zip(vpd_l, mask_l)] for vpd_l, mask_l in zip(vpd, mask)
        ]
    else:
        return vpd
