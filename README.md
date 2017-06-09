# bayesdb-flask
Simple Flask layer on top of BayesDB for anomaly detection 

Predictive probability can be used as a metric for detecting anomalous values in data. This app uses BayesDB to compute predictive probabilities of the values in a given column in a csv file. The user specifies the bdb file, population, and table for an existing model, which is used to compute predictive probabilities of the values in the user-specified column of the uploaded csv. The uploaded csv must have the same columns as the existing table. The predictive probabilities are appended to the csv file, which can then be downloaded.
