import calendar
import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = list()
    label = list()
    with open(filename) as file:
        contents = csv.DictReader(file)
        total_columns = len(contents.fieldnames)
        for data in contents:
            normalized_data = normalize(data)
            evidence.append(normalized_data[:total_columns - 2])
            label.append(normalized_data[total_columns - 1])
    return evidence, label


def normalize(data):
    month_name = list(calendar.month_abbr)
    row = list()
    for key, value in data.items():
        if should_convert_int(key):
            row.append(int(value))
        elif should_convert_float(key):
            row.append(float(value))
        elif key == "Month":
            row.append(5 if value == "June" else month_name.index(value) - 1)
        elif key == "Weekend" or key == "Revenue":
            row.append(1 if value == "TRUE" else 0)
        elif key == "VisitorType":
            row.append(1 if value == "Returning_Visitor" else 0)
    return row


def should_convert_int(column_name):
    columns = ["Administrative", "Informational", "ProductRelated",
               "OperatingSystems", "Browser", "Region", "TrafficType"]
    return column_name in columns


def should_convert_float(column_name):
    columns = ["Administrative_Duration", "Informational_Duration", "ProductRelated_Duration",
               "BounceRates", "ExitRates", "PageValues", "SpecialDay"]
    return column_name in columns


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    total_testing_data = len(predictions)
    correct_predicted_positive_label = 0.0
    correct_predicted_negative_label = 0.0
    positive_labels = 0.0
    negative_labels = 0.0

    for i in range(total_testing_data):
        if labels[i] == 1.0:
            positive_labels += 1.0
            correct_predicted_positive_label += 1.0 if labels[i] == predictions[i] else 0.0
        else:
            negative_labels += 1.0
            correct_predicted_negative_label += 1.0 if labels[i] == predictions[i] else 0.0

    sensitivity = correct_predicted_positive_label / positive_labels
    specificity = correct_predicted_negative_label / negative_labels

    return sensitivity, specificity


if __name__ == "__main__":
    main()
