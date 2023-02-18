# Import Google Api Library and required libraries
from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import client, file, tools
from pprint import pprint

# NOTE: Lines 10 - 29 are available to view on Google's guide for the Google Form API

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
# This will open a link in our browser, requesting permission using the SCOPES initialized earlier.
creds = None
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)

forms = build('forms', 'v1', http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC,
                  static_discovery=False)

form_responses = forms.forms().responses().list(formId=form_id).execute()
form_info = forms.forms().get(formId=form_id).execute()
# We can assume that everyone answers each question, since they are all required
questions_ids = [x for x in form_responses['responses'][0]['answers']]
#print(questions_ids)
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
    for x in range(len(form_info['items'])):
        all_questions[form_info['items'][x]['questionItem']['question']['questionId']] = form_info['items'][x]['title']
    # Return all questions with corresponding ID
    return all_questions


def get_number_of_responses():
    """Returns the total number of responses to the Google Form."""
    # Number of responses
    number_of_responses = len(form_responses)
    return number_of_responses



def compare_questions(independent, dependent):
    """
    Collects the number of answers to an independent question with respect to their answer to a dependent question
    For example, this function returns a dictionary with the frequencies of answers of different groups between two
    questions, allowing for data to be analyzed effectively and quickly.

    {'!!Independant Questions': 'Age',
     '!Dependant Question': 'Have you used ChatGPT?',
     '18 - 22': {'No': 1},
     'Under 18': {'No': 1, 'Yes': 2}}

    """
    hold_data = {'!Dependant Question': get_google_form_data()[dependent],
                 '!!Independant Questions': get_google_form_data()[independent]}
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
    return hold_data








    # Get dependant variables
            # pprint(form_responses['responses'][x]['answers'][y]['textAnswers']['answers'][0]['value'])
#pprint(form_responses['responses'])




#print(get_google_form_data())
#print(compare_questions(1,2))
#get_google_form_data()
#pprint(form_info)
#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
#pprint(get_google_form_data())
#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
pprint(compare_questions(questions_ids[1],questions_ids[2]))
