import re

# A class for managing SPICE model parameters.
class ParameterDictionary(dict):

    def __init__(self):
        super().__init__(self)


    def write_file(self, filename):
        # Write all parameters to a file in SPICE format
        with open(filename, 'w') as f:
            for key, value in self.items():
                f.write('+ {:s}={:.3E}\n'.format(key, value))

    def load_file(self, filename):
        # Clear the existing contents and load parameters from a file
        self.clear()

        with open(filename, 'r') as f:
            # Regular expressions for parsing parameter lines in SPICE format
            s1 = r'([a-zA-Z_][a-zA-Z_0-9]*)'
            s2 = r'([+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)'
            s3 = r'(a|f|p|n|u|m|K|Meg|G|T)?'
            pattern = r'\+[ \t]*'+(s1)+r'[ \t]*=[ \t]*'+(s2)+(s3)

            # Dictionary for converting SI prefixes to their multiplier values
            SI_prefix = {'a':1E-18, 'f':1E-15, 'p':1E-12, 'n':1E-09, 'u':1E-06, 'm':1E-03,\
                    'K':1E+03, 'Meg':1E+06, 'G':1E+09, 'T':1E+12}

            for line in f:
                # Match each line against the pattern
                m = re.match(pattern, line)
                if m:
                    # Extract parameter name, value, and optional prefix
                    m1 = m.group(1) # Parameter name
                    m2 = m.group(2) # Numeric value
                    m3 = m.group(3) # SI prefix (if present)

                    # Convert and store the value, applying the prefix if necessary
                    if m3:
                        self[m1] = float(m2)*SI_prefix[m3]
                    else:
                        self[m1] = float(m2)
