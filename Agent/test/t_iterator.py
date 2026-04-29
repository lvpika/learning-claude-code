class T_Iterator:
    def __init__(self, start: int) -> None:
        self.start = start
    
    def __iter__(self):
        return self

    def __next__(self):
        value = self.start
        self.start = self.start - 1
        if self.start < 0:
            raise StopIteration
        return value

for i in T_Iterator(10):
    print(i)