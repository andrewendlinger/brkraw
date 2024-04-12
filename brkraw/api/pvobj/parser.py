import re
import numpy as np
from collections import OrderedDict, defaultdict
from copy import copy

# REGEX patterns
ptrn_param          = r'^\#\#(?P<key>.*)\=(?P<value>.*)$'
ptrn_key            = r'^\$(?P<key>.*)'
ptrn_array          = r"\((?P<array>[^()]*)\)"
ptrn_complex_array  = r"\((?P<comparray>\(.*)\)$"
ptrn_comment        = r'\$\$.*'
ptrn_float          = r'^-?\d+\.\d+$'
ptrn_engnotation    = r'^-?[0-9.]+e-?[0-9.]+$'
ptrn_integer        = r'^[-]*\d+$'
ptrn_string         = r'^\<(?P<string>[^>]*)\>$'
ptrn_arraystring    = r'\<(?P<string>[^>]*)\>[,]*'
ptrn_bisstring      = r'\<(?P<string>\$Bis[^>]*)\#\>'
ptrn_braces         = r'\((?P<contents>[^()]*)\)'
# Paravision 360 related. @[number of repititions]([number]) ex) @5(0)
ptrn_at_array       = r'@(\d*)\*\(([-]?\d*[.]?\d*[eE]?[-]?\d*?)\)'

# Conditional enum
HEADER = 0
PARAMETER = 1


class Parser: 
    """
    Parser class for handling parameter dictionaries.

    This class provides methods for loading parameters from a list of strings, converting strings to specific data types, cleaning up array elements, processing complex arrays, parsing shapes, parsing data, parsing array data, and converting data to specified shapes.

    Methods:
        load_param: JCAMP DX parser that loads parameters from a list of strings.
        convert_string_to: Converts a string to a specific data type if it matches certain patterns.
        clean_up_elements_in_array: Cleans up array elements by replacing patterns with repeated values.
        process_bisarray: Determines the case of an array with BIS prefix by converting each element to a specific data type.
        process_complexarray: Process a complex array and return a parsed dictionary.
        process_string: Process a string and return the parsed data based on its shape.
        parse_shape: Parse the shape of the data.
        parse_data: Parse the data based on its format.
        parse_array_data: Parse the array data.
        convert_data_to: Convert the given data to the specified shape.
    """
    @staticmethod
    def load_param(stringlist):
        """JCAMP DX parser that loads parameters from a list of strings.

        Args:
            stringlist (list): A list of strings containing parameter information.

        Returns:
            params (OrderedDict): An ordered dictionary containing the parsed parameters, where the key is the line number and the value is a tuple of the parameter type, key, and value.
            param_addresses (list): A list of line numbers where parameters were found.
            stringlist (list): The original list of strings.
        """
        params = OrderedDict()
        param_addresses = []
        compiled_ptrn_param = re.compile(ptrn_param)
        compiled_ptrn_key = re.compile(ptrn_key)

        for line_num, line in enumerate(stringlist):
            if regex_obj := compiled_ptrn_param.match(line):
                key = regex_obj['key']
                value = regex_obj['value']
                if compiled_ptrn_key.match(key):
                    key = re.sub(ptrn_key, r'\g<key>', key)
                    params[line_num] = (PARAMETER, key, value)
                else:
                    params[line_num] = (HEADER, key, value)
                param_addresses.append(line_num)
        return params, param_addresses, stringlist


    @staticmethod
    def convert_string_to(string):
        """Converts a string to a specific data type if it matches certain patterns.

        Args:
            string (str): The string to be converted.

        Returns:
            float, int, or str or None: The converted value of the string, or None if the string is empty.
        """
        string = string.strip()
        if re.match(ptrn_string, string):
            string = re.sub(ptrn_string, r'\g<string>', string)
        if not string:
            return None
        if re.match(ptrn_float, string) or re.match(ptrn_engnotation, string):
            return float(string)
        elif re.match(ptrn_integer, string):
            return int(string)
        return string

    @staticmethod
    def clean_up_elements_in_array(data):
        """Cleans up array elements by replacing patterns with repeated values.

        Args:
            elements (list): A list of array elements with patterns.

        Returns:
            list: The cleaned up array elements.
        """
        elements = re.findall(ptrn_at_array, data)
        elements = list(set(elements))
        for str_ptn in elements:
            num_cnt = int(str_ptn[0])
            num_repeat = float(str_ptn[1])
            str_ptn = f"@{str_ptn[0]}*({str_ptn[1]})"

            str_replace_old = str_ptn
            str_replace_new = [num_repeat for _ in range(num_cnt)]
            str_replace_new = str(str_replace_new)
            str_replace_new = str_replace_new.replace(",", "")
            str_replace_new = str_replace_new.replace("[", "")
            str_replace_new = str_replace_new.replace("]", "")
            data = data.replace(str_replace_old, str_replace_new)
        return data

    @staticmethod
    def process_bisarray(elements, shape):
        """Determines the case of an array with BIS prefix by converting each element to a specific data type.

        Args:
            elements (list): A list of elements representing a bisarray.

        Returns:
            float, int, or list: The converted elements of the bisarray. If there is only one element, it is returned as is, otherwise a list of converted elements is returned.
        """
        elements = [Parser.convert_string_to(c) for c in elements]
        elements = elements.pop() if len(elements) == 1 else elements
        if isinstance(shape, list) and shape[0] == len(elements):
            elements = [e.split(',') for e in elements]
        return elements

    @staticmethod
    def process_complexarray(data):
        """
        Process a complex array and return a parsed dictionary.

        Args:
            data: The complex array to be processed.

        Returns:
            dict: A dictionary containing the parsed data.

        Examples:
            >>> data = [1, [2, 3], [[4, 5], [6, 7]]]
            >>> process_complexarray(data)
            {'level_1': [[1]], 'level_2': [[2, 3]], 'level_3': [[4, 5], [6, 7]]}
        """
        data_holder = copy(data)
        parser = defaultdict(list)
        level = 1
        while re.search(ptrn_braces, data_holder):
            for parsed in re.finditer(ptrn_braces, data_holder):
                cont_parser = [Parser.convert_data_to(cont.strip(), -1) for cont in parsed.group('contents').split(',') if Parser.convert_data_to(cont.strip(), -1) is not None]
                parser[f'level_{level}'].append(cont_parser)
            data_holder = re.sub(ptrn_braces, '', data_holder)
            level += 1
        return dict(parser)
    
    @staticmethod
    def process_string(data, shape):
        """
        Process a string and return the parsed data based on its shape.

        Args:
            data: The string to be processed.
            shape: The shape of the data.

        Returns:
            tuple: A tuple containing the parsed data and an empty string, or the processed string.

        Examples:
            >>> data = "[1, 2, 3]"
            >>> shape = "(3,)"
            >>> process_string(data, shape)
            ([1, 2, 3], '')

            >>> data = "Hello, World!"
            >>> shape = ""
            >>> process_string(data, shape)
            'Hello, World!'
        """
        shape = Parser.parse_shape(shape)
        if elements := re.findall(ptrn_bisstring, data):
            data = Parser.process_bisarray(elements, shape)
            return data, -1
        else:
            data = Parser.clean_up_elements_in_array(data)
        if re.match(ptrn_complex_array, data):
            data = Parser.process_complexarray(data)
        elif re.match(ptrn_string, data):
            data = re.sub(ptrn_string, r'\g<string>', data)
        else:
            data = Parser.parse_data(data)
        return data, shape

    @staticmethod
    def parse_shape(shape):
        """
        Parse the shape of the data.

        Args:
            shape: The shape of the data.

        Returns:
            str: The parsed shape.

        Raises:
            ValueError: If the shape is invalid.

        Examples:
            >>> shape = "(3, 4)"
            >>> parse_shape(shape)
            '3, 4'

            >>> shape = "3, 4"
            >>> parse_shape(shape)
            '3, 4'

            >>> shape = "(3, 4, 5)"
            >>> parse_shape(shape)
            '3, 4, 5'

            >>> shape = "(3, 4,)"
            >>> parse_shape(shape)
            ValueError: Invalid shape: (3, 4,)
        """
        if shape != -1:
            shape = re.sub(ptrn_array, r'\g<array>', shape)
            if ',' in shape:
                return [Parser.convert_string_to(c) for c in shape.split(',')]
        return shape

    @staticmethod
    def parse_data(data):
        """
        Parse the data based on its format.

        Args:
            data: The data to be parsed.

        Returns:
            list or str: The parsed data.

        Examples:
            >>> data = "[1, 2, 3]"
            >>> parse_data(data)
            [1, 2, 3]

            >>> data = "1, 2, 3"
            >>> parse_data(data)
            [1, 2, 3]

            >>> data = "1 2 3"
            >>> parse_data(data)
            [1, 2, 3]

            >>> data = "Hello, World!"
            >>> parse_data(data)
            'Hello, World!'
        """
        if matched := re.findall(ptrn_array, data):
            return Parser.parse_array_data(matched)
        elif ',' in data:
            return [Parser.convert_string_to(c) for c in data.split(',')]
        elif ' ' in data:
            return [Parser.convert_string_to(c) for c in data.split(' ')]
        return data

    @staticmethod
    def parse_array_data(matched):
        """
        Parse the array data.

        Args:
            matched: A list of strings representing the matched array data.

        Returns:
            list: The parsed array data.

        Examples:
            This method is intended to be called internally within the class and does not have direct usage examples.
        """
        if any(',' in cell for cell in matched):
            return [[Parser.convert_string_to(c) for c in cell.split(',')] for cell in matched]
        return [Parser.convert_string_to(c) for c in matched]

    @staticmethod
    def convert_data_to(data, shape):
        """
        Convert the given data to the specified shape.

        Args:
            data: The data to be converted.
            shape: The desired shape of the data.

        Returns:
            object: The converted data.

        Examples:
            This method is intended to be called internally within the class and does not have direct usage examples.
        """
        if isinstance(data, str):
            data, shape = Parser.process_string(data, shape)
        if isinstance(data, list):
            if (
                isinstance(shape, list)
                and not any(isinstance(c, str) for c in data)
                and all(c is not None for c in data)
            ):
                data = np.asarray(data).reshape(shape)
        elif isinstance(data, str):
            data = Parser.convert_string_to(data)
        return data


class Parameter:
    """
    Paravision Parameter object

    This class extends the Parser class and provides methods to initialize the object with a stringlist of parameter dictionaries, retrieve the parameters and headers, and process the contents of the data.

    Args:
        stringlist: A list of strings containing the parameter dictionaries.

    Examples:
        >>> stringlist = ["param1", "param2"]
        >>> parameter = Parameter(stringlist)

    Attributes:
        parameters (property): Get the parameters of the data.
        headers (property): Get the headers of the data.

    Methods:
        _process_contents: Process the contents of the data based on the given parameters.
        _set_param: Set the parameters and headers based on the given data.
    """
    def __init__(self, stringlist, name, scan_id=None, reco_id=None):
        """
        Initialize the Parameter object with the given stringlist, name, scan_id, and reco_id.

        Args:
            stringlist: A list of strings containing the parameter dictionaries.
            name: The name of the Parser object.
            scan_id: The scan ID associated with the Parser object.
            reco_id: The reco ID associated with the Parser object.

        Examples:
            >>> stringlist = ["param1", "param2"]
            >>> name = "MyParser"
            >>> scan_id = 12345
            >>> reco_id = 67890
            >>> parser = Parser(stringlist, name, scan_id, reco_id)
        """
        self._name = name
        self._repr_items = []
        if scan_id:
            self._repr_items.append(f'scan_id={scan_id}')
        if reco_id:
            self._repr_items.append(f'reco_id={reco_id}')
        self._set_param(*Parser.load_param(stringlist))

    @property
    def name(self):
        if '_' in self._name:
            return ''.join([s.capitalize() for s in self._name.split('_')])
        return self._name.capitalize()

    @property
    def parameters(self):
        """
        Get the parameters of the data.

        Returns:
            OrderedDict: The parameters of the data.

        Examples:
            This property can be accessed directly on an instance of the class to retrieve the parameters.
        """
        return self._parameters

    @property
    def header(self):
        """
        Get the headers of the data.

        Returns:
            OrderedDict: The headers of the data.

        Examples:
            This property can be accessed directly on an instance of the class to retrieve the headers.
        """
        return self._header

    def _process_contents(self, contents, addr, addr_diff, index, value):
        """
        Process the contents of the data based on the given parameters.

        Args:
            contents: The contents of the data.
            addr: The address of the current parameter.
            addr_diff: The difference in addresses between parameters.
            index: The index of the current parameter.
            value: The value of the current parameter.

        Returns:
            tuple: A tuple containing the processed data and its shape.

        Examples:
            This method is intended to be called internally within the class and does not have direct usage examples.
        """
        if addr_diff[index] > 1:
            c_lines = contents[(addr + 1):(addr + addr_diff[index])]
            data = " ".join([line.strip() for line in c_lines if not re.match(ptrn_comment, line)])
            return (data, value) if data else (Parser.convert_string_to(value), -1)
        return Parser.convert_string_to(value), -1

    def _set_param(self, params, param_addr, contents):
        """
        Set the parameters and headers based on the given data.

        Args:
            params: A list of parameter information.
            param_addr: The addresses of the parameters.
            contents: The contents of the data.

        Raises:
            ValueError: If an invalid dtype is encountered.

        Examples:
            This method is intended to be called internally within the class and does not have direct usage examples.
        """
        addr_diff = np.diff(param_addr)
        self._contents = contents
        self._header = OrderedDict()
        self._parameters = OrderedDict()
        for index, addr in enumerate(param_addr[:-1]):
            dtype, key, value = params[addr]
            data, shape = self._process_contents(contents, addr, addr_diff, index, value)
            if dtype is PARAMETER:
                self._parameters[key] = Parser.convert_data_to(data, shape)
            elif dtype is HEADER:
                self._header[key] = data
            else:
                raise ValueError("Invalid dtype encountered in _set_param")

    def __getitem__(self, key):
        return self.parameters[key]
    
    def __getattr__(self, key):
        return self.parameters[key]
    
    def __repr__(self):
        return f"{self.name}({', '.join(self._repr_items)})"

    def keys(self):
        return self.parameters.keys()