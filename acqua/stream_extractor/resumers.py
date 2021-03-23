import pickle


class AbstractResumer:

    def save(self, *args, **kwargs):
        raise NotImplementedError

    def _dump(self):
        with open(self.__class__.__name__, 'wb')as outfile:
            pickle.dump(self, outfile)

    def load(self):
        try:
            with open(self.__class__.__name__, 'rb')as infile:
                res = pickle.load(infile)
            return res
        except:
            return self


class LastIdResumer(AbstractResumer):

    last_id = 0

    def save(self, last_id, *args, **kwargs):
        self.last_id = last_id
        self._dump()
