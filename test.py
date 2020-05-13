import os

path, dirs, files = next(os.walk("d:/cs50/workspace/flasksqlalchemy/static/images"))
file_count = len(files)
print(file_count)