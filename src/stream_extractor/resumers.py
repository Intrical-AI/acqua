class AbstractResumer:

    def save(self, *args, **kwargs):
        raise NotImplementedError


class ElasticSearchResumer(AbstractResumer):

    def __getstate__(self):
        return super().__getstate__()

    def __setstate__(self):
        return super().__setstate__()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
