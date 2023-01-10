from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder

class EasyShopping(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('shopping.easy.intent')
    def handle_shopping_easy(self, message):
        self.speak_dialog('shopping.easy')

    @intent_handler('view.goods.intent')
    def handle_view_goods(self, message):
        self.speak('Taking a photo now. Please wait a second for me to get the result.')
        self.speak('I find some goods here, you can ask me whatever goods you want.')

    @intent_handler('is.there.any.goods.intent')
    def handle_is_there_any_goods(self, message):
        category_label = message.data.get('category')
        str = 'yes, I find ' +  category_label + ' in front of you'
        self.speak(str)

#######################################
# FAQ using Adapt Intent
#######################################

    @intent_handler(IntentBuilder('FAQ').require('FAQ_AI').build())
    def handle_ask_item_brand(self, message):
        self.speak('Easy shopping assistance is for blind people')
        self.speak('Easy shopping assistance can guild and help blind people with their shopping')


#######################################
# FAQ using Padatious Intent
#######################################
    @intent_handler('FAQ.PI.intent')
    def handle_esa_faq_pi(self, message):
        category_label = message.data.get('key')
        str = category_label + ' is for blind people. It can guild and help blind people with their shopping'
        self.speak(str)

def create_skill():
    return EasyShopping()

