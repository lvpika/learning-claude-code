import pathlib

# base_url 是一个迭代器？
base_url = pathlib.Path('.')
p = base_url.rglob("*.py")
for f in base_url.rglob("*.py"):
    f.is_file()


