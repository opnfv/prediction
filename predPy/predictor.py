#!/usr/bin/python3

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

"""Summary of models here.

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
# import tempfile
# from shutil import rmtree
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import SVMWithSGD
# from pyspark.mllib.classification import SVMModel
from pyspark.mllib.classification import LogisticRegressionWithSGD
from pyspark.mllib.classification import LogisticRegressionWithLBFGS
# from pyspark.mllib.classification import LogisticRegressionModel
from pyspark.mllib.classification import NaiveBayes
# from pyspark.mllib.classification import NaiveBayesModel
from pyspark.mllib.tree import DecisionTree
# from pyspark.mllib.tree import DecisionTreeModel
from pyspark.mllib.tree import RandomForest
# from pyspark.mllib.tree import RandomForestModel
from pyspark.mllib.tree import GradientBoostedTrees
# from pyspark.mllib.tree import GradientBoostedTreesModel


def loadRecord(line):
    """Load a CSV line and select 26 indicative parameters"""
    inputLine = StringIO.StringIO(line)
    reader = csv.reader(inputLine)
    parameters = reader.next()
    # Instances that were collected within seven days before the failures
    # are used to train the failing model
    # if float(parameters[-1]) == 1 and float(parameters[3]) >= 360:
    #    parameters[-1] = 0
    selectedParameters = (
        parameters[12:17] + parameters[19:20] + parameters[23:26] +
        parameters[39:47] + parameters[54:61] + parameters[62:]
    )
    # selectedParameters = parameters
    return selectedParameters


def parseLine(line):
    """Parse a row """
    label = float(line[-1])
    features = Vectors.dense(map(float, line[:-1]))
    return LabeledPoint(label, features)


if __name__ == "__main__":

    sc = SparkContext(appName="HardDriveFailurePrediction")

    # $example on$
    data = (sc.textFile('hdd/harddrive1.csv').map(loadRecord).
            map(parseLine))

    print("===== Choose SVM model =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a SVM model
    model = SVMWithSGD.train(trainingData, iterations=200, regParam=7e-2,
                             intercept=True)

    # Make prediction and test accuracy.
#    labelsAndPredictions = (testData
#        .map(lambda p: (p.label, model.predict(p.features))))
#    accuracy = (labelsAndPredictions
#        .filter(lambda (x, v): x == v).count() / float(testData.count()))
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of SVM model is: %.4f" % accuracy)
    print("The test recall of SVM model is: %.4f" % recall)
    print("The test fprate of SVM model is: %.4f\n\n" % fprate)

    print("===== Choose Logistic Regression model with SGD algorithm =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a logistic regression model
    model = LogisticRegressionWithSGD.train(trainingData, iterations=200,
                                            regParam=8e-2, intercept=True)

    # Make prediction and test accuracy.
    print("The original threshold: %0.2f" % float(model.threshold))
    model.setThreshold(0.40)
    print("The current threshold: %0.2f" % float(model.threshold))
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of Logistic Regression model with"
          " SGD algorithm is: %.4f" % accuracy)
    print("The test recall of Logistic Regression model with"
          " SGD algorithm is: %.4f" % recall)
    print("The test fprate of Logistic Regression model with"
          " SGD algorithm is: %.4f\n\n" % fprate)

    print("===== Choose Logistic Regression model with LBFGS algorithm =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a logistic regression model
    model = LogisticRegressionWithLBFGS.train(trainingData, iterations=200,
                                              regParam=7e-2, intercept=True)

    # Make prediction and test accuracy.
    print("The original threshold: %0.2f" % float(model.threshold))
    model.setThreshold(0.45)
    print("The current threshold: %0.2f" % float(model.threshold))
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of Logistic Regression model with"
          " LBFGS algorithm is: %.4f" % accuracy)
    print("The test recall of Logistic Regression model with"
          " LBFGS algorithm is: %.4f" % recall)
    print("The test fprate of Logistic Regression model with"
          " LBFGS algorithm is: %.4f\n\n" % fprate)

    print("===== Choose Multinomial Naive Bayes model =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a multinomial naive Bayes model given an RDD of LabeledPoint.
    model = NaiveBayes.train(trainingData, 7e-1)

    # Make prediction and test accuracy.
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of Multinomial Naive Bayes "
          "is: %.4f" % accuracy)
    print("The test recall of Multinomial Naive Bayes "
          "is: %.4f" % recall)
    print("The test fprate of Multinomial Naive Bayes "
          "is: %.4f\n\n" % fprate)

    print("===== Choose Decision Tree  model =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a decision tree model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
    model = DecisionTree.trainClassifier(trainingData, numClasses=2,
                                         categoricalFeaturesInfo={},
                                         impurity='entropy', maxDepth=4,
                                         maxBins=32)
    # print('Learned classification tree model:')
    # print(model.toDebugString())

    # Make prediction and test accuracy.
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of decision tree model is: %.4f" % accuracy)
    print("The test recall of decision tree model is: %.4f" % recall)
    print("The test fprate of decision tree model is: %.4f\n\n" % fprate)

    print("===== Choose Random Forest model =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a Random Forest model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
    # Note: Use larger numTrees in practice.
    # Setting featureSubsetStrategy="auto" lets the algorithm choose.
    model = RandomForest.trainClassifier(trainingData, numClasses=2,
                                         categoricalFeaturesInfo={},
                                         numTrees=15,
                                         featureSubsetStrategy="auto",
                                         impurity='gini', maxDepth=12,
                                         maxBins=32)
    # print('Learned classification tree model:')
    # print(model.toDebugString())

    # Make prediction and test accuracy.
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of random forest model is: %.4f" % accuracy)
    print("The test recall of random forest model is: %.4f" % recall)
    print("The test fprate of random forest model is: %.4f\n\n" % fprate)

    print("===== Choose Gradient Boosted Trees model =====")
    # Split data aproximately into training (80%) and test (20%)
    trainingData, testData = data.randomSplit([0.8, 0.2], seed=0)

    # Train a GradientBoostedTrees model.
    # Empty categoricalFeaturesInfo indicates all features are continuous.
    model = GradientBoostedTrees.trainClassifier(trainingData,
                                                 categoricalFeaturesInfo={},
                                                 numIterations=20, maxDepth=8,
                                                 maxBins=32)
    # print('Learned classification tree model:')
    # print(model.toDebugString())

    # Make prediction and test accuracy.
    predictions = model.predict(testData.map(lambda x: x.features))
    labelsAndPredictions = testData.map(lambda p: p.label).zip(predictions)
    tp = labelsAndPredictions.filter(lambda (v, p): v == p and p == 1).count()
    tn = labelsAndPredictions.filter(lambda (v, p): v == p and p == 0).count()
    fp = labelsAndPredictions.filter(lambda (v, p): v != p and p == 1).count()
    fn = labelsAndPredictions.filter(lambda (v, p): v != p and p == 0).count()
    accuracy = (labelsAndPredictions.filter(lambda (v, p): v == p).
                count() / float(testData.count()))
    print("true positive number: %d, false positive number: %d" % (tp, fp))
    print("false negative number: %d, true negative number: %d" % (fn, tn))
    recall = tp / float(tp + fn)
    fprate = fp / float(fp + tn)
    print("The test accuracy of Gradient Boosted Trees "
          "model is: %.4f" % accuracy)
    print("The test recall of Gradient Boosted Trees "
          "model is: %.4f" % recall)
    print("The test fprate of Gradient Boosted Trees "
          "model is: %.4f" % fprate)


# Save and load model
#    path = tempfile.mkdtemp(dir='.')
#    model.save(sc, path)
#    sameModel = SVMModel.load(sc, path)
#    sameModel = LogisticRegressionModel.load(sc, path)
#    sameModel = NaiveBayesModel.load(sc, path)
#    sameModel = DecisionTreeModel.load(sc, path)
#    sameModel = RandomForestModel.load(sc, path)
#    sameModel = GradientBoostedTreesModel.load(sc, path)
#    try:
#        rmtree(path)
#    except OSError:
#        pass
