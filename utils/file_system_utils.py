import os
import re
import shutil


def check_directory(parent_dir, dir_name, auto_create=False):
    """
    判断在parent_dir目录下是否存在名为dir_name的文件夹。
    如果auto_create为True，且文件夹不存在，则创建该文件夹。

    参数:
    parent_dir -- 要检查的父目录路径（字符串）
    dir_name -- 要检查的文件夹名称（字符串）
    auto_create -- 如果为True，当文件夹不存在时，自动创建该文件夹（布尔值）

    返回:
    如果文件夹存在或已创建则返回True，否则返回False
    """
    # 完整路径
    full_path = os.path.join(parent_dir, dir_name)

    # 检查路径是否存在，并且是一个目录
    if not os.path.isdir(full_path):
        if auto_create:
            os.makedirs(full_path)
            return True
        else:
            # 如果auto_create为False，且目录不存在，则返回False
            return False

    # 如果目录已经存在，返回True
    return True

def file_exists(directory, filename):
    """
    检查指定目录下是否存在名为filename的文件。

    参数:
    - directory: 目录的路径，可以是绝对路径或相对路径。
    - filename: 要检查的文件名。

    返回:
    - True: 如果文件存在。
    - False: 如果文件不存在。
    """
    return os.path.isfile(os.path.join(directory, filename))

def copy_and_rename_directory(source_dir, target_dir):
    # 检查目标目录是否存在
    if os.path.exists(target_dir):
        raise Exception(f"目标目录 {target_dir} 已经存在。")
    # 检查源目录是否存在
    if not os.path.exists(source_dir):
        raise Exception(f"源目录 {source_dir} 不存在。")
    # 复制源目录到目标目录
    shutil.copytree(source_dir, target_dir)


def find_files_matching_pattern(directory, pattern):
    """
    查找指定目录下所有文件名符合给定正则表达式pattern的文件。

    参数:
    directory -- 需要搜索的目录路径
    pattern -- 正则表达式对象或字符串

    返回:
    匹配文件名的列表
    """
    # 确保传入的是一个字符串
    if not isinstance(directory, str):
        raise ValueError("目录路径必须是字符串类型")

    # 检查目录是否存在
    if not os.path.exists(directory):
        raise ValueError(f"目录 {directory} 不存在")

    # 将正则表达式字符串转换为正则表达式对象
    if isinstance(pattern, str):
        regex = re.compile(pattern)
    elif isinstance(pattern, re.Pattern):
        regex = pattern
    else:
        raise ValueError("pattern参数必须是字符串或re.Pattern对象")

    # 获取目录下的所有文件和文件夹的名称
    all_items = os.listdir(directory)

    # 筛选出文件并检查文件名是否与正则表达式匹配
    matching_files = [item for item in all_items if os.path.isfile(os.path.join(directory, item)) and regex.match(item)]

    return matching_files