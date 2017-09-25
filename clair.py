from __future__ import print_function
import random


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    print("session_attributes: " + str(session_attributes))
    print("speechlet_response: " + str(speechlet_response))
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Hi, I'm Clair, your clairvoyant medical diagnostician. " \
                    "I will ask you a series of questions to determine your condition. " \
                    "Please answer them with yes or no. " \
                    "Are you ready to begin?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Are you ready to begin?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_disease_sublist(answers):
    current_list = disease_symptoms.keys()
    symptoms = answers.keys()
    for symptom in symptoms:
        if answers[symptom] == "Yes":
            good_list = symptom_diseases[symptom]
            for disease in current_list:
                if disease not in good_list:
                    current_list.remove(disease)
        else:
            bad_list = symptom_diseases[symptom]
            for disease in current_list:
                if disease in bad_list:
                    current_list.remove(disease)
    return current_list

def get_next_symptom(possible_diseases, symptoms_remaining):
    diseases_remaining = len(possible_diseases)
    symptom_count = {}
    for symptom in symptoms_remaining:
        symptom_count[symptom] = 0
    for disease in possible_diseases:
        symptom_list = disease_symptoms[disease]
        for symptom in symptom_list:
            if symptom in symptom_count:
                symptom_count[symptom] = symptom_count[symptom] + 1
    best_symptom = None
    for symptom in symptom_count:
        if best_symptom is None:
            best_symptom = symptom
        elif abs(
                symptom_count[symptom] -
                diseases_remaining / 2
            ) < abs(
                symptom_count[best_symptom] -
                diseases_remaining / 2
            ):
            best_symptom = symptom
    return best_symptom



def ask_next_question(answers, intent, session):
    session_attributes = session["attributes"]
    current_symptom = session_attributes["current_symptom"]
    symptoms_remaining = session_attributes["symptoms_remaining"]
    symptoms_remaining.remove(current_symptom)
    possible_diseases = get_disease_sublist(answers)
    if len(possible_diseases) == 0:
        session_attributes = {
            "guessed" : "Yes"
        }
        card_title = "Negative Identification"
        speech_output = "I was unable to diagnose your condition. " \
                        "I would advise seeking professional help to determine your condition. " \
                        "Would you like to play again?"
        reprompt_text = "Sorry, please repeat your answer. Would you like to play again?" 
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
    if len(possible_diseases) == 1:
        session_attributes = {
            "guessed" : "Yes"
        }
        card_title = "Guess"
        speech_output = "You may have " + possible_diseases[0] + ". Would you like to play again?"
        reprompt_text = "Sorry, please repeat your answer. Would you like to play again?" 
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

    else:
        current_symptom = get_next_symptom(possible_diseases, symptoms_remaining)
        session_attributes = {
            "started_questions": "Yes",
            "previous_answers": answers,
            "symptoms_remaining": symptoms_remaining,
            "current_symptom": current_symptom
        }
        card_title = "Question"
        speech_output = symptom_question[current_symptom]
        reprompt_text = "Sorry, please repeat your answer. " + symptom_question[current_symptom]
        should_end_session = False
        return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))

def handle_yes_response(intent, session):
    session_attributes = session["attributes"]
    current_symptom = session_attributes["current_symptom"]
    previous_answers = {}
    if "previous_answers" in session_attributes:
        previous_answers = session_attributes["previous_answers"]
    previous_answers[current_symptom] = "Yes"

    return ask_next_question(previous_answers, intent, session)

def handle_no_response(intent, session):
    session_attributes = session["attributes"]
    current_symptom = session_attributes["current_symptom"]
    previous_answers = {}
    if "previous_answers" in session_attributes:
        previous_answers = session_attributes["previous_answers"]
    previous_answers[current_symptom] = "No"
    return ask_next_question(previous_answers, intent, session)
    

def ask_first_question(intent, session):
    started_questions = "Yes"
    symptoms_remaining = symptom_diseases.keys()
    current_symptom = symptoms_remaining[random.randint(0, len(symptoms_remaining) - 1)]
    previous_answers = {}
    session_attributes = {
        "started_questions": started_questions,
        "previous_answers": previous_answers,
        "symptoms_remaining": symptoms_remaining,
        "current_symptom": current_symptom
    }
    card_title = "Question"
    speech_output = symptom_question[current_symptom]
    reprompt_text = "Sorry, please repeat your answer. " + symptom_question[current_symptom]
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Remember, I can only provide an educated guess for your medical condition. " \
                    "You should still seek a professional medical opinion if you feel something is wrong. " \
                    "Thanks for consulting me! I hope to speak with you soon."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    print(str(session))
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AMAZON.YesIntent":
        if "attributes" not in session:
            return ask_first_question(intent, session)
        elif "guessed" in session["attributes"]:
            return get_welcome_response()
        else:
            return handle_yes_response(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        if "attributes" not in session:
            return get_welcome_response()
        elif "guessed" in session["attributes"]:
            return handle_session_end_request()
        else:
            return handle_no_response(intent, session)
    elif intent_name == "AMAZON.StartOverIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])