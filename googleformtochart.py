# Import Python graphing library and pandas for data compilation
import matplotlib.pyplot as plt
import pandas as pd
# Import Google Api Library and required libraries
from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import client, file, tools
# For easier viewing of JSON data
from pprint import pprint


# NOTE: Lines 16 - 40 are available to view on Google's documentation for the Google Form API
# Available here: https://developers.google.com/forms/api/quickstart/python

# Scopes asked for oauth. Requesting access to forms and responses
SCOPES = ["https://www.googleapis.com/auth/forms.body.readonly",
          "https://www.googleapis.com/auth/forms.responses.readonly"]

# Google Form I.D. of the Google Form we are using
form_id = "<FORM_ID>"

# API Key - Restricted to Google Forms API v1
developerKey = "<API_KEY>"
DISCOVERY_DOC = f"https://forms.googleapis.com/$discovery/rest?version=v1"

# Store oauth token in a file 'token.json'
store = file.Storage('token.json')
# If we do not have credentials, retrieve it from credentials.json
# NOTE: credentials.json was made in the Google Developer Panel
# This will open a link in our browser, requesting permission using the SCOPES initialized earlier
creds = None
if not creds or creds.invalid:
    # Complete authorization flow
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

forms = build('forms', 'v1', http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

form_responses = forms.forms().responses().list(formId=form_id).execute()
form_info = forms.forms().get(formId=form_id).execute()
# We can assume that everyone answers each question, since they are all required
questions_ids = []
for qid in range(len(form_info['items'])):
    questions_ids.append(form_info['items'][qid]['questionItem']['question']['questionId'])

# Standard discovery.build for the Google API
# Retrieves our Google Form information, formatting the questions and responses into lists
def get_google_form_data():
    """
    Returns a dictionary of each question with their corresponding question I.D.
    """
    # Get Google Form information
    # List to hold questions
    all_questions = {}
    # Iterate through the JSON data from the above request (line 35), appending all questions to the list above
    for qname in range(len(form_info['items'])):
        all_questions[form_info['items'][qname]['questionItem']['question']['questionId']] = form_info['items'][qname]['title']
    # Return all questions with corresponding ID
    return all_questions


def get_number_of_responses():
    """

    :return: Number of Google form responses.
    """
    number_of_responses = len(form_responses['responses'])
    return number_of_responses

def get_question_data(questionID):
    """

        :param questionID: Question responses and data
        :return: EXAMPLE: {'Yes': 79, 'Not sure': 15, 'No': 12}

        Collects and organizes question responses into a dictionary ready to be plotted.
        """
    hold_data = {'!!Question': get_google_form_data()[questionID]}
    for x in range(len(form_responses['responses'])):
        if form_responses['responses'][x]['answers'][questionID]['textAnswers']['answers'][0]['value'] not in hold_data:
            hold_data[form_responses['responses'][x]['answers'][questionID]['textAnswers']['answers'][0]['value']] = 1
        else:
            hold_data[form_responses['responses'][x]['answers'][questionID]['textAnswers']['answers'][0]['value']] += 1
    return hold_data

def plotPiChart(data):
    # Data to plot
    labels = []
    sizes = []
    question = data['!!Question']
    del data['!!Question']
    for x, y in data.items():
        labels.append(x)
        sizes.append(y)

    # Plot
    plt.title(question, fontsize=8)
    plt.pie(sizes, labels=labels, autopct='%1.0f%%', pctdistance=0.9,textprops={'fontsize': 8})
    question = question.replace(" ","").replace("'", "").replace("?","").replace(",", "")
    plt.axis('equal')
    plt.savefig(f"{question}.png", format='png', dpi=500)
    print("SUCCESS: Graph plotted.")
    plt.close()


def compare_questions(independent, dependent):
    """

    :param independent: Independent question responses and data
    :param dependent: Dependent question responses and data
    :return: {'!!Independant Question': 'Age','!Dependant Question': 'Have you used ChatGPT?','18 - 22': {'No': 1},
    'Under 18': {'No': 1, 'Yes': 2}}

    Collects the number of answers to an independent question with respect to their answer to a dependent question
    For example, this function returns a dictionary with the frequencies of answers of different groups between two
    questions, allowing for data to be analyzed effectively and quickly
    """
    hold_data = {'!Dependant Question': get_google_form_data()[dependent],
                 '!!Independant Question': get_google_form_data()[independent]}
    # Iterate through each response
    for x in range(len(form_responses['responses'])):
        # Create a key of the answer of the independent variable if it is not already in the dictionary Add the
        # current responses answer as a value to the key, making it a key of a sub-dictionary. This will allow for the
        # function to count the frequency of responses of certain groups, allowing for optimal data collection
        if form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value'] not in hold_data:
            hold_data[
                form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']] = {}
            if form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value'] not in \
                    hold_data[
                        form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']]:
                hold_data[form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']][
                    form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value']] = 1
            else:
                hold_data[form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']][
                    form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value']] += 1
        else:
            # If the independent group is already present within the dict, we only need to update the frequency of their
            # answer to the dependant question
            if form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value'] not in \
                    hold_data[
                        form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']]:
                hold_data[form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']][
                    form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value']] = 1
            else:
                hold_data[form_responses['responses'][x]['answers'][independent]['textAnswers']['answers'][0]['value']][
                    form_responses['responses'][x]['answers'][dependent]['textAnswers']['answers'][0]['value']] += 1

    # FIXES INCORRECT GRAMMAR IN QUESTION ID: 1ed26975
    # Changing the value in the Google Form did not transfer the results, thus we must manually fix it here.
    # To fix this problem, we simply identify each occurrence of the mistake and change it by creating a new key
    # with the fixes and deleting the old one after its values copied to the fixed one.
    if independent == '1ed26975':
        hold_data['I have a bit of knowledge about it.'] = hold_data['I have a bit knowledge about it.']
        del hold_data['I have a bit knowledge about it.']
    if dependent == '1ed26975':
        for response in hold_data.keys():
            if response == '!Dependant Question' or response == '!!Independant Question':
                continue
            else:
                hold_data[response]['I have a bit of knowledge about it.'] = hold_data[response]['I have a bit knowledge about it.']
                del hold_data[response]['I have a bit knowledge about it.']

    return hold_data


def plotGraph(data, graphType: str, stacked: bool, xlabel: str, ylabel: str):
    """

    :param data: Google form data.
    :param graphType: Select between 'bar' or 'line'.
    :param stacked: True for stacked bar graph, False for grouped bar graph.
    :return: Saves a graph of the desired type to the project directory.

    Given the data dictionary from the compare_questions function. This function compiles the data and plots a
    grouped bar graph using matplotlib and pandas
    """
    hold_questions = []
    hold_questions.append([data["!!Independant Question"], data["!Dependant Question"]])
    # Get Q1 labels
    q1_labels = list(data.keys())
    del data["!!Independant Question"]
    del data["!Dependant Question"]
    q1_labels.remove("!!Independant Question")
    q1_labels.remove("!Dependant Question")
    # Get Q2 value labels
    q2_labels = list(data.values())
    q2_labelsFinal = set()
    for values in q2_labels:
        for label in values:
            q2_labelsFinal.add(label)

    # Normalize data (If an option has 0 answers, display that (Google Forms API does not do this automatically))
    for value in data.values():
        for label in q2_labelsFinal:
            if label not in value:
                value[label] = 0

    # Plot graph
    df = pd.DataFrame(data)

    # Create a graph with dimensions of 14" x 9"
    if graphType == 'line':
        ax = df.T.plot(kind=graphType, figsize=(16, 9), stacked=stacked)
    else:
        ax = df.T.plot(kind=graphType, figsize=(14, 9), stacked=stacked, width=0.85)
    if graphType == 'bar':
        # Add values to bars (Annotate bars)
        if stacked == False:
            for container in ax.containers:
                ax.bar_label(container)
        else:
            # Add values to stacked bars, adding them to the center of each segment
            for c in ax.containers:
                # Optional: if the segment is small or 0, customize the labels
                # Remove the labels parameter if it's not needed for customized labels (height == 0)
                labels = [int(v.get_height()) if v.get_height() > 0 else '' for v in c]
                ax.bar_label(c, labels=labels, label_type='center', color='white')

    # Add the number of responses to the upper-right corner
    plt.text(1, 1.10,f"(Responses: {get_number_of_responses()})" , transform=ax.transAxes, fontsize=10,
             bbox=dict(facecolor='red', alpha=0.5))
    plt.xticks(rotation=13, ha='right', fontsize=12)
    plt.ylabel(ylabel,labelpad=20, fontsize=15)
    plt.xlabel(xlabel,labelpad=8, fontsize=15)
    plt.title(f"{hold_questions[0][1]}", fontsize=13)
    plt.legend(fontsize=13)
    plt.tight_layout()
    # To prevent file overwrites, make the file title the two questions, ensuring uniqueness
    # Also ensure that the filename is file-friendly
    fileTitleD = hold_questions[0][1].replace(" ","").replace("'", "").replace("?","").replace(",", "")
    fileTitleI = hold_questions[0][0].replace(" ","").replace("'", "").replace("?","").replace(",", "")
    # Save image to the computer as a png and pixel density of 400 pixels per inch
    plt.savefig(f"{fileTitleI}vs{fileTitleD}.png", format='png', dpi=400)
    # Process will consume too much memory if the graphs are not closed after generation.
    plt.close()
    print("SUCCESS: Graph plotted.")

    ############################################
    # Un-comment to display an interactive graph
    # plt.show()
    ############################################

print("\nQuestions and ID's")
pprint(get_google_form_data())
print(f"\nQuestion ID list:\n{questions_ids}")
print("")

# Pi charts for independent variables
plotPiChart(get_question_data(questions_ids[0]))
plotPiChart(get_question_data(questions_ids[1]))
plotPiChart(get_question_data(questions_ids[2]))
plotPiChart(get_question_data(questions_ids[3]))
plotPiChart(get_question_data(questions_ids[4]))

# PLOT: AGE VS. DEPENDENT QUESTIONS
plotGraph(compare_questions(questions_ids[0], questions_ids[10]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[8]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[-2]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[-5]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[0], questions_ids[7]), graphType='bar', stacked=False, xlabel="Age", ylabel="Number of Responses")
# PLOT: MAJOR VS. DEPENDENT QUESTIONS
plotGraph(compare_questions(questions_ids[4], questions_ids[10]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[8]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[-2]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[-5]), graphType='bar', stacked=False, xlabel="Program", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[4], questions_ids[7]), graphType='bar', stacked=True, xlabel="Program", ylabel="Number of Responses")
# PLOT: HIGHEST EDUCATION VS. DEPENDENT QUESTIONS
plotGraph(compare_questions(questions_ids[3], questions_ids[10]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[-3]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[8]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[-2]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[-5]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")
plotGraph(compare_questions(questions_ids[3], questions_ids[7]), graphType='bar', stacked=False, xlabel="Level of Education", ylabel="Number of Responses")

