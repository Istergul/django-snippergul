import os

def cache(instance, path, specname, extension):
    filepath, basename = os.path.split(path)
    filename = os.path.splitext(basename)[0]
    new_name = '%s_%s%s' % (filename, specname, extension)
    return os.path.join(filepath, new_name)
