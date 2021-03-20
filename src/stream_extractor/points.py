class AbstractPoint:

    def __init_values(self):
        raise NotImplementedError

    def __init__(self, state=None) -> None:
        if state is None:
            self._init_values()
        else:
            for k, v in state.items():
                setattr(self, k, v)

    def to_dict(self):
        raise NotImplementedError

    def __add__(self, obj):
        raise NotImplementedError


class AvgPoint(AbstractPoint):

    def _init_values(self):
        self.avg = 0
        self.total = 0

    def __call__(self, newpoint):
        self.avg = (self.avg * self.total + newpoint) / (self.total + 1)
        self.total += 1

    def __str__(self):
        return f'(Avg): {self.avg}, (Total): {self.total}'

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return{
            'avg': self.avg,
            'total': self.total
        }

    def __add__(self, obj):
        assert isinstance(obj, self.__class__), f'''Add two objects from the same class
        Not {self.__class__.__name__} and {obj.__class__.__name__}'''
        res = AvgPoint()
        res.total = self.total + obj.total
        res.avg = (self.avg * self.total + obj.avg * obj.total) / res.total
        return res


class CounterPoint(AbstractPoint):

    def _init_values(self):
        self.count = 0

    def __call__(self, newpoint):
        self.count += 1

    def __str__(self):
        return f'(Counter): {self.count}'

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return{
            'total': self.count
        }


class CountedListPoint(AbstractPoint):

    def _init_values(self):
        self.count = 0
        self.values = []

    def __call__(self, newpoint):
        self.count += 1
        self.values.append(newpoint)

    def to_dict(self):
        return{
            'total': self.count,
            'values': self.values
        }
