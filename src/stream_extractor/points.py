class AvgPoint:
    
    def __init__(self):
        self.avg = 0
        self.total = 0
        
    def __call__(self, newpoint):
        self.avg = (self.avg * self.total + newpoint) / (self.total + 1)
        self.total += 1 
    
    def __str__(self):
        return f'(Avg): {self.avg}, (Total): {self.total}'
    
    def __repr__(self):
        return self.__str__()
    
class CounterPoint:
    
    def __init__(self):
        self.avg = 0
        self.count = 0
        
    def __call__(self, newpoint):
        self.count += 1 
    
    def __str__(self):
        return f'(Counter): {self.count}'
    
    def __repr__(self):
        return self.__str__()