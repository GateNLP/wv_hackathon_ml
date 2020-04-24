import sys
from WvLibs import DataReader

raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]

dataReader = DataReader(annoed_json_dir, raw_json_file)
