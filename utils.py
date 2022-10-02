from flask import abort, make_response, jsonify

class ResourceDecorator:
    def __init__(self, resource_name):
        self.resource_name = resource_name

    def __call__(self, func):
        return self.generate_wrapped(func)

    def _set_generator(self, gen_func, pass_arguments=False):
        def generator_wrapper(func, kwargs):
            if self.resource_name not in kwargs:
                args = kwargs if pass_arguments else {}
                kwargs[self.resource_name] = gen_func(**args)
            return func(**kwargs)

        self.set_wrapper(generator_wrapper)

    def set_generator(self, gen_func=None, **kwargs):
        if not gen_func and kwargs:
            return lambda func: self._set_generator(func, **kwargs)
        elif gen_func:
            return self._set_generator(gen_func)
        else:
            raise Exception('!')

    def set_wrapper(self, wrapper):
        if getattr(self, 'wrapper_func', False):
            raise AttributeError(f'Wrapper function for {self.resource_name} already set')
        self.wrapper_func = wrapper

    def generate_wrapped(self, func):
        try:
            wrapper_func = self.wrapper_func
        except AttributeError:
            raise AttributeError(f'Wrapper function for {self.resource_name} not set')

        def wrapper(**kwargs):
            return wrapper_func(func, kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

def json_abort(reason):
    abort(jsonify({'status':'error', **({'reason':reason} if reason else {})}), 400)

