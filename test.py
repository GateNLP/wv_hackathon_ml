import sys
from WvLibs import WVdataIter, ReaderPostProcessor

raw_json_file = sys.argv[1]
annoed_json_dir = sys.argv[2]

postProcessor = ReaderPostProcessor()

dataIter = WVdataIter(annoed_json_dir, raw_json_file, postProcessor=postProcessor.postProcess)
print(next(dataIter))
print(next(dataIter))
#for item in dataIter:
#    print(item)

#dataReader = DataReader(annoed_json_dir, raw_json_file)
