### Based on a TSPLIB parser of tsartsaris
### https://github.com/tsartsaris/TSPLIB-python-parser
### Modified to parse GTSP file format

import re
from typing import List, Dict


def read_tsp_file_contents(filename: str) -> List:
    """
    gets the contents of the file into a list
    :param filename: the filename to read
    :return: a list like ['NAME: ulysses16.tsp',
                        'TYPE: TSP COMMENT: Odyssey of Ulysses (Groetschel/Padberg)',
                        'DIMENSION: 16',
                        'EDGE_WEIGHT_TYPE: GEO',
                        'DISPLAY_DATA_TYPE: COORD_DISPLAY',
                        'NODE_COORD_SECTION',
                        '1 38.24 20.42',
                        '2 39.57 26.15',..., 'EOF']
    """
    with open(filename) as f:
        content = [line.strip() for line in f.read().splitlines()]
        return content


class TSPParser:
    """
    TSP file parser to turn the TSP problem file into a dictionary of type
    {'1': (38.24, 20.42), '2': (39.57, 26.15),...}

    Usage like
    TSPParser(filename=file_name)
    print(TSPParser.tsp_cities_dict)
    """
    filename: str = None
    dimension: int = None
    nClass: int = None
    tsp_file_contents: List = []
    tsp_cities_dict: Dict = {}
    classes: List = {}

    @classmethod
    def __init__(cls, filename: str) -> None:
        cls.clear_data()
        cls.filename = filename
        cls.on_file_selected()

    @classmethod
    def on_file_selected(cls) -> None:
        """
        internal use when instantiating class object
        :return: NADA goes to open the file
        """
        cls.open_tsp_file()

    @classmethod
    def open_tsp_file(cls) -> None:
        """
        if file is tsp will read the contents
        :return: NADA assign to tsp_file_contents
        """
        cls.tsp_file_contents = read_tsp_file_contents(cls.filename)
        cls.detect_dimension()
        cls.detect_nClass()
        cls.get_cities_dict()
        cls.get_classes()

    @classmethod
    def detect_dimension(cls) -> None:
        """
        finds the list element that starts with DIMENSION and gets the int
        :return: NADA goes to get the dict
        """
        for record in cls.tsp_file_contents:
            if record.startswith("DIMENSION"):
                parts = record.split(":")
                cls.dimension = int(parts[1])
                print("Nodes: {}".format(cls.dimension))

    @classmethod
    def detect_nClass(cls) -> None:
        """
        finds the list element that starts with GTSP_SETS and gets the int
        :return: NADA goes to get the dict
        """
        for record in cls.tsp_file_contents:
            if record.startswith("GTSP_SETS"):
                parts = record.split(":")
                cls.nClass = int(parts[1])
                print("Classes: {}".format(cls.nClass))

    @classmethod
    def get_cities_dict(cls) -> None:
        """
        zero index is the index in the contents list where city coordinates starts
        last index of parser is the zero index + dimension of the file
        :return: NADA assign to tsp_cities_dict dict like {'1': (38.24, 20.42),
                                                     '2': (39.57, 26.15),...}
        """
        zero_index = cls.tsp_file_contents.index("NODE_COORD_SECTION") + 1
        for index in range(zero_index, zero_index + cls.dimension):
            parts = cls.tsp_file_contents[index].strip()
            city_coords_parts = re.findall(r"[+-]?\d+(?:\.\d+)?", parts)
#            print(city_coords_parts)
            cls.tsp_cities_dict[int(city_coords_parts[0])-1] = (float(city_coords_parts[1]), float(city_coords_parts[2]))
#       print("city coordinates:")
#       print(cls.tsp_cities_dict)


    @classmethod
    def get_classes(cls) -> None:
        """
        zero index is the index in the contents list where class section starts
        last index of parser is the zero index + number of classes
        """
        zero_index = cls.tsp_file_contents.index("GTSP_SET_SECTION") + 1
        for index in range(zero_index, zero_index + cls.nClass):
            parts = cls.tsp_file_contents[index].strip()
            class_parts = re.findall(r"[+-]?\d+(?:\.\d+)?", parts)
            class_id = int(class_parts[0])-1
            for i in range(1,len(class_parts)-1):
                if (int(class_parts[i])>0):
                    cls.classes[int(class_parts[i])-1] = class_id
#        print("classes:")
#        print(cls.classes)


    @classmethod
    def clear_data(cls) -> None:
        """
        re-use the class
        :return: NADA
        """
        cls.filename = ""
        cls.tsp_cities_dict = {}
        cls.tsp_file_contents = []
        cls.dimension = 0
        cls.nClass = 0



