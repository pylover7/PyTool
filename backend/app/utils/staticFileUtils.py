from pathlib import Path


def check_dir_exists(filePath: [str]):
    """
    检查目录是否存在，如果不存在则创建

    :param filePath: list[str] 目录路径
    :return:
    """
    for path in filePath:
        Path(path).mkdir(parents=True, exist_ok=True)
