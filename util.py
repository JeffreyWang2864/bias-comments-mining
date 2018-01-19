import re
import time
import os

PROJECT_ABS_LOCATION = os.path.dirname(os.path.abspath(__file__))

def polishChineseSentences(targets):
    polished = list()
    for target in targets:
        res = re.findall("[\u4E00-\u9FA5]+", str(target))
        plain_chinese = "".join(res)
        polished.append(plain_chinese)
    polished = list(filter(lambda x: len(set(x)) > 1, polished))
    return polished

def rest(second):
    assert isinstance(second, int)
    assert 0 < second < 100
    time.sleep(second)

def print_progress(name, percentage):
    percentage *= 100
    num_of_sharp = int(percentage/2)
    num_of_equal = 50-num_of_sharp
    strap = "[" + "#" * num_of_sharp + "=" * num_of_equal + "]"
    print("\n\nprogress of %s: %s %.2f%%\n\n"%(name, strap, percentage))
