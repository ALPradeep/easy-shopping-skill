from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context
from mycroft.util import LOG
#import random
import os
import sys
import time
from multiprocessing import Process, Queue
import csv
import json
from .cvAPI import getDetail, getObjLabel

LOGSTR = '********************====================########## '
CSV_FIELD_NAME = ['objectLabel', 'objectLogo', 'objectText', 'objectColor']
# need to be changed
CSV_FILE_NAME = '/opt/mycroft/skills/easy-shopping-skill.alfredpradeepkumar/store/store.csv'
#Path_To_Image = '/opt/mycroft/skills/easy-shopping-skill.alfredpradeepkumar/testPhoto/'


def generate_str(possible_list):
    res = ''
    if len(possible_list) == 3:
        res = possible_list[0] + ' ' + \
            possible_list[1] + ' and ' + possible_list[2]
    elif len(possible_list) == 2:
        res = possible_list[0] + ' and ' + possible_list[1]
    elif len(possible_list) == 1:
        res = possible_list[0]
        
    return res
    
def write_to_csv(row):
    with open(CSV_FILE_NAME, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELD_NAME)
        writer.writerow(row)
        f.close()

def check_category_in_csv(category):
    with open(CSV_FILE_NAME, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categorys = row['objectLabel']
            categorys = categorys.split(categorys)
            categorys = [ele.lower() for ele in categorys]
            if category in categorys:
                return row
        return {}

class EasyShopping(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.img_multi = ''
        self.category_str = ''
        self.color_str = ''
        self.brand_str = ''
        self.kw_str = ''
        self.img_hand = ''
        self.detail = ''
        self.log.info(LOGSTR + "_init_ EasyShoppingSkillEnhanced1")

    @intent_file_handler('shopping.easy.intent')
    def handle_shopping_easy(self, message):
        self.speak_dialog('shopping.easy')

#    @intent_handler('view.goods.intent')
#    def handle_view_goods(self, message):
        # self.speak('Taking a photo now. Please wait a second for me to get the result.')
        # self.speak('I find some goods here, you can ask me whatever goods you want.')

#    @intent_handler('is.there.any.goods.intent')
#   def handle_is_there_any_goods(self, message):
#        category_label = message.data.get('category')
#        str = 'yes, I find ' +  category_label + ' in front of you'
#        self.speak(str)


#######################################
# Workshop 1
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
        
#######################################
# Workshop 2 Voice Assistant Development
#######################################
# Padatious Intent
#######################################

    @intent_handler('view.goods.intent')
    def handle_view_goods(self, message):
        #self.speak_dialog('take.photo')
        self.speak_dialog('take.photo')
        self.img_multi = ''
        self.img_hand = ''

        # suppose we use camera to take a photo here, 
        # then the function will return an image path
        self.img_multi = 'Path_To_Image/multi.jpeg'

        self.speak('I find some goods here, you can ask me whatever goods you want.')
        
        
    @intent_handler('is.there.any.goods.intent')
    def handle_is_there_any_goods(self, message):
        if self.img_multi == '':
            # if self.img_multi == '', 
            # then it means that user hasn't invoked intent(handle_view_goods)
            self.handle_no_context1(message)
            
        else:
            # in real application, label_str and loc_list will return from CV API
            label_list = [['milk', 'drink', 'bottle'], ['milk', 'drink', 'bottle']]
            loc_list = ['left top', 'right top']

            category_label = message.data.get('category')
            detected = 0

            for i in range(len(label_list)):
                label_str = str(label_list[i])
                label_str = label_str.lower()
        
                if category_label is not None:
                    if category_label in label_str:
                        self.speak_dialog('yes.goods',
                                    {'category': category_label,
                                    'location': loc_list[i]})
                        detected = 1
                        break
                else:
                    continue

            if detected == 0:
                self.speak_dialog('no.goods',
                {'category': category_label})
            
            
            
    def handle_no_context1(self, message):
        self.speak('Please let me have a look at what\'s in front of you first.')
        take_photo = self.ask_yesno('do.you.want.to.take.a.photo') # This calls .dialog file.
        if take_photo == 'yes':
            self.handle_view_goods(message)
        elif take_photo == 'no':
            self.speak('OK. I won\'t take photo')
        else:
            self.speak('I cannot understand what you are saying')
            
#######################################
# Workshop Challenge
#######################################
    @intent_handler('have.bought.intent')
    def handle_have_bought(self, message):
        ask_category = message.data.get('category')
        category_detail = check_category_in_csv(ask_category)
        if category_detail: 
            # dic is not empty
            tell_detail = self.ask_yesno('do.you.want.to.know.detail.about.you.have.bought')

            if tell_detail == 'yes':
                this_category_str = generate_str(string_to_array(category_detail['objectLabel']))
                this_brand_str = generate_str(string_to_array(category_detail['objectLogo']))
                this_color_str = generate_str(get_color_array(category_detail['objectColor']))
                this_kw_str = ' '.join(string_to_array(category_detail['objectText']))

                self.speak_dialog('item.complete.info', {'category': this_category_str})
                self.handle_ask_item_detail('color', this_color_str)
                self.handle_ask_item_detail('brand', this_brand_str)
                self.handle_ask_item_detail('keyword', this_kw_str)
            else:
                self.speak('OK, I won\'t say details.')

        else:
            # dic is empty
            self.speak_dialog('do.not.bought.item', {'category': ask_category})
        
#######################################
# Adapt Intent with conversational Context
#######################################

    @intent_handler(IntentBuilder('ViewItemInHand').require('ViewItemInHandKeyWord'))
    def handle_view_item_in_hand(self, message):
        self.speak_dialog('take.photo')
        self.img_multi = ''
        self.img_hand = ''
    
        # suppose we use camera to take a photo here, 
        # then the function will return an image path
        #self.img_hand = 'Path_To_Image/2.jpeg'
        #detail = []
        
        # suppose we call CV API here to get the result, 
        # the result will all be list, then we use generate_str() to create string
#        self.category_str = str(random.choice(['milk', 'bottle', 'drink']))
        self.category_str = generate_str(['milk', 'bottle', 'drink'])
        self.brand_str = generate_str(['Dutch Lady', 'Lady'])
        self.color_str = generate_str(['white', 'black', 'blue'])
        self.kw_str = ' '.join(['milk', 'bottle', 'protein', 'pure', 'farm'])
 
        details = {'objectLabel': [self.category_str], 'objectLogo': [self.brand_str],
           'objectText': [self.kw_str], 'objectColor': [self.color_str]}
        self.detail = details
        # set the context
        self.set_context('getDetailContext')
    
        # speak dialog
        self.speak_dialog('item.category', {'category': self.category_str})
    
    def handle_ask_item_detail(self, detail, detail_str):
        if detail_str == '':
            self.speak_dialog(
            'cannot.get', {'detail': detail}, expect_response=True)
        else:
            dialog_str = 'item.' + detail
            self.speak_dialog(dialog_str, {detail: detail_str}, expect_response=True)

#    @intent_handler(IntentBuilder('ViewItemInHand').require('ViewItemInHandKeyWord'))
 #   def handle_view_item_in_hand(self, message):
  #      self.speak('Taking a photo now. Please wait a second for me to get the result.')
  #      self.speak('The item is possible to be something. You can ask me any details about the item now, such as brand, color or complete information.')
   #     #set the context
    #    self.set_context('getDetailContext')

    @intent_handler(IntentBuilder('AskItemCategory').require('Category').require('getDetailContext').build())
    def handle_ask_item_category(self, message):
        #self.speak('I am talking about the category of the item')
        self.handle_ask_item_detail('category', self.category_str)

    @intent_handler(IntentBuilder('AskItemColor').require('Color').require('getDetailContext').build())
    def handle_ask_item_color(self, message):
        #self.speak('I am talking about the color of the item')
        #self.speak_dialog('color', {'category': self.color_str})
        self.handle_ask_item_detail('color', self.color_str)
    @intent_handler(IntentBuilder('AskItemBrand').require('Brand').require('getDetailContext').build())
    def handle_ask_item_brand(self, message):
        self.handle_ask_item_detail('brand', self.brand_str)
        #self.speak('I am talking about the brand of the item')
        #self.speak_dialog('brand', {'category': self.brand_str})
        take_photo = self.ask_yesno('do.you.want.to.take.a.photo') # This calls .dialog file.
        if take_photo == 'yes':
            self.handle_ask_item_detail('brand', self.brand_str)
        elif take_photo == 'no':
            self.speak('OK. I won\'t take photo')
        else:
            self.speak('I cannot understand what you are saying')

    @intent_handler(IntentBuilder('AskItemKw').require('Kw').require('getDetailContext').build())
    def handle_ask_item_keywords(self, message):
        #self.speak('I am talking about the keywords of the item')
        #self.speak_dialog('color', {'category': self.kw_str})
        self.handle_ask_item_detail('keyword', self.kw_str)
        
    @intent_handler(IntentBuilder('AskItemInfo').require('Info').require('getDetailContext').build())
    def handle_ask_item_complete_info(self, message):
        #self.speak('I am speaking the complete information of the item')
        self.speak_dialog('item.complete.info', {'category': self.category_str})
        self.handle_ask_item_detail('color', self.color_str)
        self.handle_ask_item_detail('brand', self.brand_str)
        self.handle_ask_item_detail('keyword', self.kw_str)
        
    @intent_handler(IntentBuilder('NoContext').one_of('Category', 'Color', 'Brand', 'Kw', 'Info'))
    def handle_no_context2(self, message):
        self.speak('Please let me have a look at what\'s in your hand first.')
        
    @intent_handler(IntentBuilder('FinishOneItem').require('Finish').require('getDetailContext').build())
    @removes_context('getDetailContext')
    def handle_finish_current_item(self, message):
        if self.detail != '':
            write_to_csv(self.detail)
            self.speak('Got you request. I will put the item into cart. Let\'s continue shopping!')
            self.types_str = ''
            self.color_str = ''
            self.logo_str = ''
            self.kw_str = ''
            self.img_hand = ''
            self.img_multi = ''
        else:
            self.speak('Sorry, I don\'t understand')            



#######################################
def create_skill():
    return EasyShopping()

