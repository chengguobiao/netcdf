from netcdf import open as nc_open


class TileAdapter(object):

    def __init__(self, manager, variable):
        self.manager = manager
        self.variable = variable

    def normalized_index(self, indexes, names):
        cls = indexes.__class__
        answers = {
            slice: [indexes],
            list: indexes,
        }
        sub_i = (lambda i: slice(i, i + 1, None) if isinstance(i, int) else i)
        indexes = answers[cls] if cls in answers else map(sub_i, list(indexes))
        indexes += map(lambda i: slice(None), range(len(names) - len(indexes)))
        return indexes

    @property
    def distributed_dim(self):
        return self.manager.distributed_dim

    def dimensions_names(self):
        dims = {len(v): (k) for k, v in self.variable.dimensions.items()}
        names = filter(lambda n: n,
                       map(lambda sh: dims[sh] if sh in dims
                           else self.distributed_dim,
                           self.variable.shape))
        names = sorted(set(names), key=lambda x: names.index(x))
        return names

    def adjust_index(self, args):
        to_l = lambda s: [s.start, s.stop, s.step]
        index, tail_limits, dim_limits = (to_l(args[0]), to_l(args[1]),
                                          list(args[2]))
        absolute = lambda n: dim_limits[1] + n if n and n < 0 else n
        if tail_limits == [None, None, None]:
            tail_limits = dim_limits + tail_limits[2:]
        tail_limits = map(absolute, tail_limits)
        fix = lambda t: (dim_limits[1]
                         if t > dim_limits[1] else
                         (dim_limits[0] if t < dim_limits[0] else t))
        tail_limits = map(fix, tail_limits)
        index = map(lambda i: i if i else 0, index)
        index[0] = tail_limits[0] + index[0]
        index[1] = (tail_limits[0] + index[1]
                    if index[1] > 0 else tail_limits[1] + index[1])
        return slice(index[0], index[1], index[2] if index[2] else 1)

    def transform(self, indexes):
        names = self.dimensions_names()
        shapes = list(self.variable.shape)
        get_slice = lambda n: slice(*self.manager.dimensions.get(n, [None]))
        limits = map(lambda n: get_slice(n if n in self.manager.dimensions
                                         else self.distributed_dim), names)
        var_limits = zip([0] * len(shapes), shapes)
        related = zip(self.normalized_index(indexes, names),
                      limits,
                      var_limits)
        indexes = map(self.adjust_index, related)
        # TODO: Adapt index selection.
        if len(indexes) < len(shapes) and shapes[0] is 1:
            indexes.insert(0, slice(None))
        return tuple(indexes)

    def translate(self, indexes):
        indexes = self.transform(indexes)
        limits = self.transform(slice(None))

        def outside(args):
            l, i = args
            return (l.start and l.stop and
                    (l.start > i.start or i.stop > l.stop))
        wrong = filter(outside, zip(limits, indexes))
        if wrong:
            raise Exception('Overflow: Index outside of the tile dimensions.')
        return indexes

    def __setitem__(self, indexes, changes):
        indexes = self.translate(indexes)
        return self.variable.__setitem__(indexes, changes)

    def __getitem__(self, indexes):
        indexes = self.translate(indexes)
        return self.variable.__getitem__(indexes)

    @property
    def shape(self):
        return self[:].shape

    def copy_to(self, var):
        indexes = self.transform(slice(None, None, None))
        var[indexes] = self[:]

    def __getattr__(self, name):
        return getattr(self.variable, name)


class TileManager(object):

    def __init__(self, pattern_or_root, dimensions=None,
                 distributed_dim=None, read_only=False):
        if pattern_or_root.__class__ in [str, list]:
            pattern_or_root = nc_open(pattern_or_root, read_only=read_only)[0]
        self.root = pattern_or_root
        self.distributed_dim = distributed_dim
        self.dimensions = dimensions if dimensions else {}

    def getvar(self, *args, **kwargs):
        var = self.root.getvar(*args, **kwargs)
        return TileAdapter(self, var)

    def __getattr__(self, name):
        return getattr(self.root, name)


def tailor(pattern_or_root, dimensions=None, distributed_dim='time',
           read_only=False):
    """
    Return a TileManager to wrap the root descriptor and tailor all the
    dimensions to a specified window.

    Keyword arguments:
    root -- a NCObject descriptor.
    pattern -- a filename string to open a NCObject descriptor.
    dimensions -- a dictionary to configurate the dimensions limits.
    """
    return TileManager(pattern_or_root, dimensions=dimensions,
                       distributed_dim=distributed_dim, read_only=read_only)
