import logging
import ask_sdk_core.utils as ask_utils
import os
from ask_sdk_s3.adapter import S3Adapter
s3_adapter = S3Adapter(bucket_name=os.environ["S3_PERSISTENCE_BUCKET"])

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

import check_subway


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

NAME_TO_DESIGNATION={
    "staten island railroad": "SIR",
    "rockaway park shuttle": "H",
    "grand central shuttle": "GS",
    "forty second street shuttle": "GS",
    "40 second street shuttle": "GS",
    "franklin avenue shuttle": "FS"
}

DESIGNATION_TO_NAME={
    "SIR": "staten island railroad",
    "H": "rockaway park shuttle",
    "GS": "grand central shuttle",
    "FS": "franklin avenue shuttle"
}


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! I can check the status of your train here. Which lines do you need me to keep an eye of? Please only say one at a time."
        reprompt_text = "Which lines' status do you want me to tell you? Please just say the number or letter.\
        For shuttle lines, please just say the official name of the shuttle. For example, Franklin Avenue Shuttle. You can also say help to learn more."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt_text)
                .response
        )

class HasLinesLaunchRequestHandler(AbstractRequestHandler):
    """Handler for launch after they have set their lines"""

    def can_handle(self, handler_input):
        # extract persistent attributes and check if they are all present
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("lines" in attr)

        return attributes_are_present and ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        lines = attr['lines']

        speak_output = check_subway.check_subway(lines)
        handler_input.response_builder.speak(speak_output)

        return handler_input.response_builder.response

class CaptureLinesIntentHandler(AbstractRequestHandler):
    """Handler to capture requested trains."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("capture_train_lines")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slot = ask_utils.request_util.get_slot(handler_input, "lines")
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("lines" in attr)
        
        if attributes_are_present:
            attr = handler_input.attributes_manager.persistent_attributes
            lines = attr['lines']
        else:
            lines = []
        
        word_to_numbers={
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7
        }
        
        slot.value=slot.value.replace(".",'')
        slot.value=slot.value.lower()

        
        if slot.value in NAME_TO_DESIGNATION:
            slot.value=NAME_TO_DESIGNATION[slot.value]
        elif slot.value in word_to_numbers:
            slot.value=(str(word_to_numbers[slot.value]))
        else:
            slot.value=(slot.value.upper())
            
        if slot.value in lines:
            return (
                handler_input.response_builder
                    .speak(f"Sorry, it seems like you have added the {DESIGNATION_TO_NAME[slot.value] if slot.value in DESIGNATION_TO_NAME else slot.value} train before. Please try again.")
                    .response
            )
        
        lines.append(slot.value)
        
        attributes_manager = handler_input.attributes_manager

        lines_attributes = {
            "lines": lines
        }
        
        attributes_manager.persistent_attributes = lines_attributes
        attributes_manager.save_persistent_attributes()
        
        for index, line in enumerate(lines):
            if line in DESIGNATION_TO_NAME:
                lines[index]=DESIGNATION_TO_NAME[line]
                
        
        lines_output=', '.join(lines)

        speak_output = f'OK, I will check the status of the {lines_output} when you open the skill next time. You can add another train or say exit if you are done.'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class ClearAllLinesHandler(AbstractRequestHandler):
    """Handler to clear all trains."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("clear_all_lines")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("lines" in attr)
        
        if attributes_are_present:
            lines_attributes = {}
            attributes_manager = handler_input.attributes_manager


            attributes_manager.persistent_attributes = lines_attributes
            attributes_manager.save_persistent_attributes()
            
            speak_output = f'OK, I have cleared all trains in memory.'
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
                )
        else:
            return (
            handler_input.response_builder
                .speak("Hm, it does not seem like you have told me any trains yet.")
                .response
            )


class DeleteOneLineHandler(AbstractRequestHandler):
    """Handler to clear one of the trains."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("delete_one_line")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
                
        word_to_numbers={
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7
        }

        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("lines" in attr)
        

        if attributes_are_present:
            slot = handler_input.request_envelope.request.intent.slots["line"]

            lines = attr['lines']
            
            slot.value=slot.value.replace(".",'')
            slot.value=slot.value.lower()

            if slot.value in NAME_TO_DESIGNATION:
                slot.value=NAME_TO_DESIGNATION[slot.value]
            elif slot.value in word_to_numbers:
                slot.value=(str(word_to_numbers[slot.value]))
            else:
                slot.value=(slot.value.upper())
                
            if slot.value in lines:
                lines.remove(slot.value)
                lines_attributes = {
                            "lines": lines
                        }
                        
                attributes_manager = handler_input.attributes_manager

                attributes_manager.persistent_attributes = lines_attributes
                attributes_manager.save_persistent_attributes()
                
                speak_output = f'OK, I have deleted the {DESIGNATION_TO_NAME[slot.value] if slot.value in DESIGNATION_TO_NAME else slot.value} train.'
                
                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .response
                )
            else:
                return (
                    handler_input.response_builder
                        .speak(f"Hm, it does not seem like you have added the {DESIGNATION_TO_NAME[slot.value] if slot.value in DESIGNATION_TO_NAME else slot.value} yet.")
                        .response
                )
                
        else:
            return (
            handler_input.response_builder
                .speak("Hm, it does not seem like you have told me any trains yet.")
                .response
            ) 

class ListLinesHandler(AbstractRequestHandler):
    """Handler to list all trains."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("list_lines")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        attributes_are_present = ("lines" in attr)
        
        if attributes_are_present:
            lines = attr['lines']
            
            for index, line in enumerate(lines):
                if line in DESIGNATION_TO_NAME:
                    lines[index]=DESIGNATION_TO_NAME[line]
                    
            lines_output=', '.join(lines)

            speak_output = f'I will check the {lines_output} every time you ask me to check the subway status.'
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .response
                )
        else:
            return (
            handler_input.response_builder
                .speak("Hm, it does not seem like you have told me any trains yet.")
                .response
            )


class CheckLineHandler(AbstractRequestHandler):
    """Handler to check one line without saving."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("check_one_line")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
                
        word_to_numbers={
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7
        }
        
        slot = handler_input.request_envelope.request.intent.slots["line"]


        slot.value=slot.value.replace(".",'')
        slot.value=slot.value.lower()

        if slot.value in NAME_TO_DESIGNATION:
            slot.value=NAME_TO_DESIGNATION[slot.value]
        elif slot.value in word_to_numbers:
            slot.value=(str(word_to_numbers[slot.value]))
        else:
            slot.value=(slot.value.upper())
            
        return (
            handler_input.response_builder
                .speak(check_subway.check_subway([slot.value])+"\n Please be aware that this line is not saved into my memory. To do that, say add, and then the line you want me to remember")
                .response
        ) 


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Here's what you can say to me. You can say you want to add a certain line so that I can check the status of the line.\
        You can say check, then say what lines do you want to check to check the status of the line without me remembering it.\
        You can delete one or all of the lines I remembered. You can also say list my trains to have me list all the trains I have in memory. When you\
        are adding a shuttle or the Staten Island Railroad, just say their name. For shuttle between Times Square and Grand Central, say forty\
        second street shuttle or grand central shuttle. For shuttle between Rockaway Park and Broad Channel, say Rockaway Park Shuttle. For shuttle\
        between Franklin Avenue and Prospect Park, say Franklin Avenue Shuttle. For Staten Island Railroad, just say Staten Island Railroad. So, what do you want to do?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = CustomSkillBuilder(persistence_adapter=s3_adapter)

sb.add_request_handler(HasLinesLaunchRequestHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureLinesIntentHandler())
sb.add_request_handler(ClearAllLinesHandler())
sb.add_request_handler(DeleteOneLineHandler())
sb.add_request_handler(ListLinesHandler())
sb.add_request_handler(CheckLineHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
