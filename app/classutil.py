import new

class DynamicLoader(object):
    def __init__(self):
        self.mod_dict = {}

    def abs_import(self,mod_path):
        if not self.mod_dict.has_key(mod_path):
            mod = __import__(mod_path)
            for sub_module in mod_path.split(".")[1:]:
                mod = getattr(mod,sub_module)
            self.mod_dict[mod_path] = mod
        return self.mod_dict[mod_path]

    def addMethod(self,container,mod_name,meth_name):
        mod = self.abs_import(mod_name)
        meth_def = getattr(mod,meth_name)
        args = (meth_def,container,container.__class__)
        new_method = new.instancemethod(*args)
        setattr(container,meth_name,new_method)

    def keys():
        return mod_dict.keys()


