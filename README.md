# wv_hackathon_ml

This is created for EUvsVirus Hackathon

## Crossvalidation of baseline 
python crossvalidation.py RawJsonData Folder2AnnotatedData --configFile bert_path_config --cachePath cache_path_for_models

e.g.
python crossvalidation.py ~/Downloads/Sample_Dataset.json Allresults/ --configFile sampleConfig.cfg --cachePath /home/xingyi/wvcrossValBaselineWithSource/

## Annotation Agreement measurement
python agreementMeasure.py RawJsonData Folder2AnnotatedData agreement.tsv < --ignoreLabel label2ignore --ignoreUser annotator2ignor --min_anno_filter filterWithMinimalFrequency>

e.g.
python agreementMeasure.py Poynter_datasetv3_en.json Allresults/ agreement.tsv --ignoreLabel SocAlrm --ignoreUser 04 --min_anno_filter -1 

