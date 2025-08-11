import re

# A class for managing SPICE model parameters.
class ParameterDictionary(dict):

    def __init__(self):
        super().__init__()


    def write_file(self, filename):
        try:
            with open(filename, 'w') as f:
                for key, value in self.items():
                    f.write('+ {:s}={:.3E}\n'.format(key, value))

        except Exception as e:
            print(f"Error writing parameters to '{filename}': {e}")


    def load_file(self, filename):
        self.clear()
        try:
            with open(filename, 'r') as f:
                pattern = r'\+[ \t]*([a-zA-Z_][a-zA-Z_0-9]*)[ \t]*=[ \t]*'\
                          r'([+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)'\
                          r'(meg|a|f|p|n|u|m|k|g|t)?'

                SI_prefix = {'a':1E-18, 'f':1E-15, 'p':1E-12, 'n':1E-09, 'u':1E-06,\
                             'm':1E-03, 'k':1E+03, 'meg':1E+06, 'g':1E+09, 't':1E+12}

                for line in f:
                    m = re.search(pattern, line, re.IGNORECASE)
                    if m:
                        name, value, prefix = m.group(1), m.group(2), m.group(3)
                        multiplier = SI_prefix.get(prefix.lower(), 1) if prefix else 1
                        self[name] = float(value) * multiplier

        except Exception as e:
            print(f"Error loading parameters: {e}")
