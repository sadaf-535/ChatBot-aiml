import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle, os

model_filename = 'gender_classifier.pkl'
def predict_gender(name):
    if os.path.exists(r'E:\Maheen_Bot\gender_classifier.pkl'):
        print('trained model found')
        # Load the trained model from the pickle file
        with open(model_filename, 'rb') as file:
            vectorizer, classifier = pickle.load(file)
    else:
        print('learning model from scratch')
        # Load the dataset
        data = pd.read_csv('names_to_train.csv')  # Replace 'names.csv' with your dataset filename

        # Split the dataset into features and labels
        X = data['Name']
        y = data['Gender']

        # Split the data into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

        # Vectorize the input names
        vectorizer = CountVectorizer()
        X_train_vectorized = vectorizer.fit_transform(X_train)
        X_test_vectorized = vectorizer.transform(X_test)

        # Train the Naive Bayes classifier
        classifier = MultinomialNB()
        classifier.fit(X_train_vectorized, y_train)

        # Predict the gender for the test set
        y_pred = classifier.predict(X_test_vectorized)

        # Calculate the accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy * 100:.2f}%")

        # Save the trained model to a pickle file
        with open(model_filename, 'wb') as file:
            pickle.dump((vectorizer, classifier), file)
    # predicting gender of new name
    new_name_vectorized = vectorizer.transform([name])
    predicted_gender = classifier.predict(new_name_vectorized)

    if predicted_gender[0] == 1:
        gender = "Male"
    else:
        gender = "Female"

    return gender
