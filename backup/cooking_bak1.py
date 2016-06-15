from __future__ import print_function
import unirest, json

# --------------- Request handler ------------------
def lambdaHandler(event, context):
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

    # if event['session']['new']:
    #     on_session_started({'requestId': event['request']['requestId']},
    #                        event['session'])

    if event['request']['type'] == "LaunchRequest":
        return onLaunch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return onIntent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return onSessionEnded(event['request'], event['session'])


# def on_session_started(session_started_request, session):
#     """ Called when the session starts """
#
#     print("on_session_started requestId=" + session_started_request['requestId']
#           + ", sessionId=" + session['sessionId'])


# --------------- Request Handles ------------------
def onLaunch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want"""

    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return getWelcomeResponse()


def onIntent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your sk ill's intent handlers
    if intent_name == "getRecipeIntent":
        return getRecipe(intent, session)
    elif intent_name == "readIngredientsIntent":
        return readIngredients(intent, session)
    elif intent_name == "startRecipeIntent":
        return startRecipe(intent, session)
    elif intent_name == "nextStepIntent":
        return nextStep(intent, session)
    elif intent_name == "repeatStepIntent":
        return repeatStep(intent, session)
    elif intent_name == "previousStepIntent":
        return previousStep(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return getWelcomeResponse()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return sessionEndRequestHandle()
    else:
        raise ValueError("Invalid intent")


def onSessionEnded(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """

    print("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Functions that control the skill's behavior ------------------
def getWelcomeResponse():
    session_attributes = {}
    card_title = "Time to Cook"
    speech_output = "Let's start cooking!" + "First, tell me what you want to make."
    text_output = "Let's start cooking!" + "First, tell me what you want to make."
    reprompt_text = "Sorry, I didn't get that." + "Tell me what you want to make."
    should_end_session = False
    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))


def sessionEndRequestHandle():
    card_title = "Voila, All Done"
    speech_output = "I hope cooking with me was fun. " + "Bon appetit!"
    text_output = "I hope cooking with me was fun. " + "Bon appetit!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return buildResponse({}, buildSpeechResponse(
        card_title, speech_output, text_output, None, should_end_session))


def getRecipe(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Recipe' in intent['slots']:
        recipeName = intent['slots']['Recipe']['value']
        searchUrl = "http://food2fork.com/api/search?key=eabccd215340a8555c74ca4c1b91d0c5&page=1&q=" + recipeName
        response = unirest.get(searchUrl)
        data = response.body
        getUrl = data['recipes'][0]['source_url']
        newGetUrl = "https://spoonacular-recipe-food-nutrition-v1.p.mashape.com/recipes/extract?forceExtraction=false&url=" + getUrl
        fullRecipeResponse = unirest.get(newGetUrl, headers={"X-Mashape-Key": "ZdI3P7OSmGmshXpO0mDVMDVndgoop1jjFIGjsnJBkk43YdMgsm"})
        recipeData = fullRecipeResponse.body
        if recipeData:
            recipeIngredients = []
            for ingredient in recipeData['extendedIngredients']:
                ingredientText = ingredient['originalString']
                recipeIngredients.append(ingredientText)
            recipeInstructions = recipeData['text']
            if recipeInstructions:
                instructionsList = recipeInstructions.split('.');
            #instructionsList = [x for x in map(str.strip, recipeInstructions.split('.')) if x]

            session_attributes["recipeName"] = recipeName
            card_title = "Ingredients for " + recipeName
            session_attributes["recipeInstructions"] = instructionsList
            session_attributes["recipeFound"] = True
            session_attributes["recipeIngredients"] = recipeIngredients

            speech_output = "I found the recipe for " + recipeName + ". I sent the ingredients to your phone. " + "Would you like me to say them?"
            text_output = "Ingredients:\n"
            for ingredient in recipeIngredients:
                text_output = text_output + ingredient + "\n"

            reprompt_text = "I sent the ingredients to your phone. " + " Would you like me to say them?"
    else:
        speech_output = "I'm not sure I know how to cook that. " + "Want to to try something else?"
        text_output = "I'm not sure I know how to cook that. " + "Want to to try something else?"
        reprompt_text = "I'm not sure I know how to cook that. " + "Want to to try something else?"
    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))


def readIngredients(intent, session):

    card_title = "Read Ingredients Aloud for " + session["attributes"]["recipeName"]
    session_attributes = session["attributes"]
    should_end_session = False
    speech_output = ""
    ingredientsList = session["attributes"]["recipeIngredients"]

    if session["attributes"]["recipeFound"] == True:
        for ingredient in ingredientsList:
            speech_output += ingredient
        text_output = ""
        reprompt_text = "Are we ready to start cooking?"
    else:
        speech_output = "I don't understand what you're saying, bro."
        text_output = "I don't understand what you're saying, bro."
        reprompt_text = "I don't understand what you're saying, bro."
    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))


def startRecipe(intent, session):

    card_title = session["attributes"]["recipeName"]
    session_attributes = session["attributes"]
    should_end_session = True

    if session["attributes"]["recipeFound"] == True:
        recipeText = session["attributes"]["recipeInstructions"]
        if recipeText:
            should_end_session = False
            session_attributes["currentStep"] = 0
            currentStep = session_attributes["currentStep"]

            speech_output = recipeText[currentStep]
            text_output = recipeText[currentStep]
            reprompt_text = recipeText[currentStep]
        else:
            speech_output = "There are no instructions for this recipe."
            text_output = "There are no instructions for this recipe."
            reprompt_text = "There are no instructions for this recipe."
    else:
        speech_output = "You need to search for a recipe first."
        text_output = "You need to search for a recipe first."
        reprompt_text = "You need to search for a recipe first."

    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))

def nextStep(intent, session):

    session_attributes = session["attributes"]
    should_end_session = False

    recipeText = session["attributes"]["recipeInstructions"]
    currentStep = session["attributes"]["currentStep"]
    currentStep += 1
    card_title = "Step " + `currentStep + 1`

    if currentStep > 0 and currentStep < len(recipeText):

        session_attributes["currentStep"] = currentStep
        speech_output = recipeText[currentStep]
        text_output = recipeText[currentStep]
        reprompt_text = recipeText[currentStep]

    else:
        if currentStep <= 0:
            should_end_session = True
            speech_output = "First, we need a recipe to cook!"
            text_output = "First, we need a recipe to cook!"
            reprompt_text = "First, we need a recipe to cook!"
        if currentStep > len(recipeText):
            should_end_session = True
            speech_output = "All done. Enjoy your meal."
            text_output = "All done. Enjoy your meal."
            reprompt_text = "All done. Enjoy your meal."

    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))


def repeatStep(intent, session):

    session_attributes = session["attributes"]
    should_end_session = False

    recipeText = session["attributes"]["recipeInstructions"]
    currentStep = session["attributes"]["currentStep"]
    card_title = "Step " + `currentStep + 1`

    if currentStep >= 0 and currentStep < len(recipeText):

        session_attributes["currentStep"] = currentStep
        speech_output = recipeText[currentStep]
        text_output = recipeText[currentStep]
        reprompt_text = recipeText[currentStep]

    else:
        if currentStep < 0:
            should_end_session = True
            speech_output = "First, we need a recipe to cook!"
            text_output = "First, we need a recipe to cook!"
            reprompt_text = "First, we need a recipe to cook!"
        if currentStep > len(recipeText):
            should_end_session = True
            speech_output = "All done. Enjoy your meal."
            text_output = "All done. Enjoy your meal."
            reprompt_text = "All done. Enjoy your meal."

    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))

def previousStep(intent, session):

    session_attributes = session["attributes"]
    should_end_session = False

    recipeText = session["attributes"]["recipeInstructions"]
    currentStep = session["attributes"]["currentStep"]
    currentStep -= 1
    card_title = "Step " + `currentStep + 1`

    if currentStep >= 0 and currentStep < len(recipeText):

        session_attributes["currentStep"] = currentStep
        speech_output = recipeText[currentStep]
        text_output = recipeText[currentStep]
        reprompt_text = recipeText[currentStep]

    else:
        if currentStep < 0:
            if session["attributes"]["recipeFound"] == True:
                currentStep += 1
                session_attributes["currentStep"] = currentStep
                card_title = "Step " + `currentStep + 1`
                should_end_session = False
                speech_output = recipeText[currentStep]
                text_output = recipeText[currentStep]
                reprompt_text = recipeText[currentStep]
            else:
                should_end_session = True
                speech_output = "First, we need a recipe to cook!"
                text_output = "First, we need a recipe to cook!"
                reprompt_text = "First, we need a recipe to cook!"
        if currentStep > len(recipeText):
            should_end_session = True
            speech_output = "All done. Enjoy your meal."
            text_output = "All done. Enjoy your meal."
            reprompt_text = "All done. Enjoy your meal."

    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, text_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------
def buildSpeechResponse(title, output, text_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': text_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def buildResponse(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }