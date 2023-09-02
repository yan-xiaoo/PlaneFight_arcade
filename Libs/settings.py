import json


# -- 规定飞机难度的部分 --
SCORE_DIFFICULTY = [[0, 100, 0], [100, 150, 1], [150, 200, 2],
                    [200, 300, 3], [300, 400, 4]]


def load_difficulty(path: str):
    """
    读取难度文件
    :param path: 难度文件的路径，字符串
    :return: 定义难度的字典
    """
    with open(path, 'r') as f:
        return json.load(f)


def get_difficulty(score: int):
    """
    通过当前得分获取难度等级
    :param score: 当前的得分
    :return: 得分对应的难度等级
    """
    for i in SCORE_DIFFICULTY:
        if i[0] <= score < i[1]:
            return i[2]
    return 4
