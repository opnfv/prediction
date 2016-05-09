# Copyright (c) 2016 Huawei
# All Rights Reserved.
#
#   Licensed to the Apache Software Foundation (ASF) under one or more
#   contributor license agreements.  See the NOTICE file distributed with
#   this work for additional information regarding copyright ownership.
#   The ASF licenses this file to You under the Apache License, Version 2.0
#   (the "License"); you may not use this file except in compliance with
#   the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

"""
SVM
Logistic Regression with SGD
Logistic Regression with LBFGS
Multinomial Naive Bayes
Decision Tree
Random Forest
Gradient Boosted Trees
"""
from __future__ import print_function

from pyspark import SparkContext

import csv
import StringIO

import tempfile
from shutil import rmtree

# from pyspark.mllib.classification import SVMWithSGD, SVMModel
from pyspark.mllib.classification import LogisticRegressionWithSGD
# from pyspark.mllib.classification import LogisticRegressionWithLBFGS
from pyspark.mllib.classification import LogisticRegressionModel
# from pyspark.mllib.classification import NaiveBayes, NaiveBayesModel
# from pyspark.mllib.tree import DecisionTree, DecisionTreeModel
# from pyspark.mllib.tree import RandomForest, RandomForestModel
# from pyspark.mllib.tree import GradientBoostedTrees, GradientBoostedTreesModel
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint


def loadRecord(line):
    """Load a CSV line and select 26 indicative parameters"""
    input = StringIO.StringIO(line)
    reader = csv.reader(input)
    parameters = reader.next()
    # Instances that were collected within seven days before the failures
    # are used to train the failing model
    if parameters[3] >= 168:
        parameters[-1] = 0
    selectedParameters = parameters[12:17] + parameters[19:20] \
        + parameters[23:26] + parameters[39:47] + parameters[54:61] \
        + parameters[62:]
    return selectedParameters


def parseLine(line):
    """Parse a row """
    label = float(line[-1])
    features = Vectors.dense(map(float, line[:-1]))
    return LabeledPoint(label, features)


if __name__ == "__main__":

    sc = SparkContext(appName="HardDriveFailurePrediction")

    # $example on$
    data = sc.textFile('hdd/harddrive1.csv').map(loadRecord)\
        .map(parseLine)

    # Split data aproximately into training (60%) and test (40%)
    [trainingData, testData] = data.randomSplit([0.6, 0.4], seed=0)

    # Train a SVM model
#    model = SVMWithSGD.train(trainingData, iterations=2)
    # Train a logistic regression model
    model = LogisticRegressionWithSGD.train(trainingData, iterations=3)
#    model = LogisticRegressionWithLBFGS.train(trainingData)
    # Train a multinomial naive Bayes model given an RDD of LabeledPoint.
#    model = NaiveBayes.train(trainingData, 0.8)
    # Train a decision tree model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
#    model = DecisionTree.trainClassifier(trainingData, numClasses=2,
#                                         categoricalFeaturesInfo={},
#                                         impurity='entropy', maxDepth=5,
#                                         maxBins=32)
    # Train a RandomForest model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
    # Note: Use larger numTrees in practice.
    # Setting featureSubsetStrategy="auto" lets the algorithm choose.
#    model = RandomForest.trainClassifier(trainingData, numClasses=2,
#                                         categoricalFeaturesInfo={},
#                                         numTrees=3,
#                                         featureSubsetStrategy="auto",
#                                         impurity='gini', maxDepth=7,
#                                         maxBins=32)

    # Train a GradientBoostedTrees model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
#    model = GradientBoostedTrees.trainClassifier(trainingData,
#                                                 categoricalFeaturesInfo={},
#                                                 numIterations=3, maxDepth=3,
#                                                 maxBins=32)
    # Make prediction and test accuracy.
#    labelsAndPredictions = testData\
#        .map(lambda p: (p.label, model.predict(p.features)))
#    accuracy = labelsAndPredictions\
#        .filter(lambda (x, v): x == v).count() / float(testData.count())
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    accuracy = labelsAndPredictions.filter(lambda (v, p): v == p).\
        count() / float(testData.count())
    print('Test Accuracy = ' + str(accuracy))
#    print('Learned classification tree model:')
#    print(model.toDebugString())

    # Save and load model
    path = tempfile.mkdtemp(dir='.')
    model.save(sc, path)
#    sameModel = SVMModel.load(sc, path)
    sameModel = LogisticRegressionModel.load(sc, path)
#    sameModel = NaiveBayesModel.load(sc, path)
#    sameModel = DecisionTreeModel.load(sc, path)
#    sameModel = RandomForestModel.load(sc, path)
#    sameModel = GradientBoostedTreesModel.load(sc, path)
    try:
        rmtree(path)
    except OSError:
        pass
