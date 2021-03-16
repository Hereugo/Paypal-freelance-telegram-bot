import random
class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    if isinstance(v, list):
                        self.__convert(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                elif isinstance(v, list):
                    self.__convert(v)
                self[k] = v

    def __convert(self, v):
        for elem in range(0, len(v)):
            if isinstance(v[elem], dict):
                v[elem] = Map(v[elem])
            elif isinstance(v[elem], list):
                self.__convert(v[elem])

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

def getFromArrDict(arr, name, val):
    for x in arr:
        if x[name] == val:
            return x
    return None

def formatTime(x):
    return '{} days {} hours {} minutes {} seconds'.format(x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec) 

def toSeconds(x):
    return x * 24 * 60 * 60

def newId():
    return ''.join(random.choice(string.ascii_uppercase) for i in range(12))

def previous(path):
    return re.search(r'(.+\/)+', path)[0][:-1]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False