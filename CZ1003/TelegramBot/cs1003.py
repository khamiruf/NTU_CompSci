import time
import telepot
import apiai
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telepot.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id
#  use webhook to get answer from API.AI


def smart_chat(msg):
    CLIENT_ACCESS_TOKEN = 'f369bf2737564c009ab84bc25562bb69'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'
    request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
    request.query = msg
    response = request.getresponse()
    dic = response.read().decode('utf-8').split(',')
    for el in dic:
        if 'fulfillment' in el:
            ans = el.split('"')[5]
    if len(ans) == 0:  # if no answer is given, just tell users to ask other questions
        ans = "Sorry I don't understand. Please try again!"
    return ans


class BookStore(object):
    def __init__(self):
        # we created small database for testing
        self._database = {384822958: [{'publisher': 'Oxford University Press', 'contact info': '90596962', 'author': 'Bhasin, Harsh', 'price': '25', 'title': 'Algorithms: design and analysis', 'edition': '', 'year of publication': '2015', 'condition': '99'},
            {'publisher': '', 'contact info': '90596962', 'author': 'Quang Cuong Pham', 'price': '23', 'title': 'Introduction to Control Theory', 'edition': '', 'year of publication': '', 'condition': '100'},
            {'publisher': 'Pearson', 'contact info': '90596962', 'author': 'Harrison - Horngren - Thomas -Surwardy', 'price': '20', 'title': 'Financial Accounting', 'edition': '9th', 'year of publication': '', 'condition': '70'},
            {'publisher': 'McGraw Hill', 'contact info': '90596962', 'author': 'Suss - Unisim', 'price': '25', 'title': 'Managerial Accounting', 'edition': '', 'year of publication': '', 'condition': '100'},
            {'publisher': 'O\'Reily', 'contact info': '90596962', 'author': 'Jeff Cogswell', 'price': '30', 'title': 'C++ Cookbook', 'edition': '', 'year of publication': '2005', 'condition': '90'},
            {'publisher': 'O\'Reily Media', 'contact info': '90596962', 'author': 'Powers - Shelly', 'price': '24', 'title': 'JavaScript cookbook : programming the web', 'edition': '2nd', 'year of publication': '2015', 'condition': '90'},
            {'publisher': 'Dulles, Virginia : Mercury Learning and Information', 'contact info': '90596962', 'author': 'Parker - Jim R.', 'price': '30', 'title': 'Python : an introduction to programming', 'edition': '', 'year of publication': '2017', 'condition': '100'},
            {'publisher': 'Berkeley, CA : Apress : Imprint: Apress', 'contact info': '90596962', 'author': 'Sutherland - Bruce', 'price': '19', 'title': 'C++ Recipes: A Problem-Solution Approach', 'edition': '', 'year of publication': '2015', 'condition': '80'},
            {'publisher': 'Berkeley, CA : Apress : Imprint: Apress', 'contact info': '90596962', 'author': 'Horton - Ivor', 'price': '15', 'title': 'Beginning C++', 'edition': '', 'year of publication': '2014', 'condition': '80'},
            {'publisher': 'Hoboken, NJ : John Wiley', 'contact info': '90596962', 'author': 'Koffman - Elliot B.', 'price': '15', 'title': 'Data structures : abstraction and design using Java', 'edition': '', 'year of publication': '2010', 'condition': '80'},
            {'publisher': 'Boston, Mass. : Thomson/Course Technology', 'contact info': '90596962', 'author': 'Gilberg - Richard F.', 'price': '15', 'title': 'Data structures : a pseudocode approach with C', 'edition': '', 'year of publication': '2005', 'condition': '70'},
            {'publisher': 'Reading, Mass. : Addison-Wesley Pub. Co.', 'contact info': '90596962', 'author': 'William J. Collins', 'price': '5', 'title': 'Data structures : an object-oriented approach', 'edition': '', 'year of publication': '1992', 'condition': '50'},
            {'publisher': 'Cambridge University Press', 'contact info': '90596962', 'author': 'Peter Brass', 'price': '15', 'title': 'Advanced Data Structures', 'edition': '', 'year of publication': '2008', 'condition': '90'}]}
    # this function is used for adding provided book info from sellers into database

    def book_info(self, seller_id, book_info):
        try:
            self._database[seller_id].append(book_info)
        except KeyError:
            self._database[seller_id] = []
            self._database[seller_id].append(book_info)


book_store = BookStore()


class ChatHandler(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatHandler, self).__init__(*args, **kwargs)
        self._old_msg = ''
        self._sell_info_flag = False   # self._sell_info_flag is True when users provide book info
        self._buy_info_flag = False    # self._buy_info_flag is True when users search for books
        self._buy_or_not = False       # self._buy_or_not is True when users decide buy any book or not
        self._title_flag = False       # self._title_flag is True when users enter the title of book
        self._author_flag = False      # self._title_flag is True when users enter the author of book
        self._edition_flag = False
        self._year_flag = False
        self._publisher_flag = False
        self._price_flag = False
        self._condition_flag = False
        self._contact_flag = False
        self._continue_provide_info = True
        self._looking_for_title = '///'
        self._looking_for_author = '///'
        self._looking_for_contact = '///'
        self._book_info = {}
        self._seller_matched_list = []
        self._book_matched_list = []
        self._input_type_list = ['title', 'author', 'edition', 'year of publication', 'publisher', 'price', 'condition', 'contact info']
        for i in self._input_type_list:
            self._book_info[i] = ''
    # this function is used for getting data from sellers         

    def get_input(self, input_type, content_type, chat_id, msg):
        input_type_list = ['title', 'author', 'edition', 'year of publication', 'publisher', 'price', 'condition', 'contact info']
        count = 0
        command_input_list = ['Title', 'Author', 'Edition', 'Year of Publication', 'Publisher', 'Price in SGD', 'Condition in %', 'Contact Infomation']
        if content_type == 'text':
            if msg['text'] not in command_input_list: 
                index = input_type_list.index(input_type)
                if index == 0:
                    self._title_flag = False
                elif index == 1:
                    self._author_flag = False
                elif index == 2:
                    self._edition_flag = False
                elif index == 3:
                    self._year_flag = False
                elif index == 4:
                    self._publisher_flag = False
                elif index == 5:
                    self._price_flag = False
                elif index == 6:
                    self._condition_flag = False
                else:
                    self._contact_flag = False

                if msg['text'] not in 'no':
                    self._book_info[input_type] = msg['text']
                    bot.sendMessage(chat_id, 'I got your input. Thanks')
                    print(self._book_info)
                    for i in ['title', 'author', 'condition', 'price', 'contact info']:
                        if self._book_info[i] != '':
                            count += 1
                    if count == 5 and self._continue_provide_info == True:          
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Yes', callback_data='Yes')],
                            [InlineKeyboardButton(text='No', callback_data='No')]])
                        bot.sendMessage(chat_id, 'It seems I have enough infomation. Do you wanna continue providing infomation?', reply_markup=keyboard)
                        self._continue_provide_info = False
                    else:
                        keyboard = ReplyKeyboardMarkup(keyboard=[
                           [KeyboardButton(text='Title'), KeyboardButton(text='Author')],
                           [KeyboardButton(text='Edition'), KeyboardButton(text='Year of Publication')],
                           [KeyboardButton(text='Publisher'), KeyboardButton(text='Condition in %')],
                           [KeyboardButton(text='Price in SGD'), KeyboardButton(text='Contact Infomation')]], one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, 'You can click other tabs to provide more infomation or click old tabs to change infomation',
                                        reply_markup=keyboard)
   
                else:
                    keyboard = ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text='Title'), KeyboardButton(text='Author')],
                        [KeyboardButton(text='Edition'), KeyboardButton(text='Year of Publication')],
                        [KeyboardButton(text='Publisher'), KeyboardButton(text='Condition in %')],
                        [KeyboardButton(text='Price in SGD'), KeyboardButton(text='Contact Infomation')]], one_time_keyboard=True, resize_keyboard=True)
                    bot.sendMessage(chat_id, 'Okay, I understand but I need more infomation. Please click other tabs. Thanks so much.', reply_markup=keyboard)
        else:
            bot.sendMessage(chat_id, 'Please help me to correctly provide the '+ str(input_type) + '. If you don\'t want to make it please say \'no\'. Many thanks')
    # search any book in database based on users' inputs

    def search(self, title, author, chat_id):
        book_available = []
        title_matching = []
        seller_matching = []
        list_seller = book_store._database.keys()
        list_search_key_title = list(map(lambda x:x.encode('utf-8').lower(), title.split(' ')))
        list_search_key_author = list(map(lambda x:x.encode('utf-8').lower(), author.split(' ')))
        print(list_search_key_author)
        print(list_search_key_title)

        # searching based on title of book
        for seller in list_seller:
            list_book = book_store._database[seller]
            for book in list_book:
                count_title = 0
                for search_key_title in list_search_key_title:
                    if search_key_title in book['title'].encode('utf-8').lower():
                        count_title += 1
                if count_title >= 1:
                    title_matching.append(book)
                    seller_matching.append(seller)
                    
        
        # searching based on author of book
        for book in title_matching:
            count_author = 0
            for search_key_author in list_search_key_author:
                if search_key_author in book['author'].encode('utf-8').lower():
                    count_author += 1
            if count_author >= 1:
                book_available.append(book)
        if len(title_matching) == 0:
            bot.sendMessage(chat_id, 'Sorry! I can not found any book available for you')
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Yes', callback_data='search_other_book_yes')],
                            [InlineKeyboardButton(text='No', callback_data='search_other_book_no')]])
            bot.sendMessage(chat_id, 'Do you wanna search for other books?', reply_markup=keyboard)
        else:
            self._seller_matched_list = seller_matching
            self._book_matched_list = title_matching
            if len(book_available) == 0:
                book_available = title_matching
            bot.sendMessage(chat_id, 'Here is the list of results: ')
            for i in range(len(book_available)):
                bot.sendMessage(chat_id, str(i+1) + '. Title: ' + str(book_available[i]['title']   + '\n' + 'Author: ' + str(book_available[i]['author']) + '\n'+ 'Condition: ' + str(book_available[i]['condition']) + '% \n' + 'Price: ' + str(book_available[i]['price']) + ' SGD \n' + 'Edition: ' + str(book_available[i]['edition']) + '\n' + 'Year of Publication: ' + str(book_available[i]['year of publication']) + '\n' + 'Publisher: ' + str(book_available[i]['publisher']) + '\n' + 'Contact Infomation: ' + str(book_available[i]['contact info']) + ' \n \n \n'))

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Yes', callback_data='buy_book_yes')],
                [InlineKeyboardButton(text='No', callback_data='buy_book_no')]])    
            bot.sendMessage(chat_id, 'Do you wanna buy any book above?', reply_markup=keyboard)
    # notify seller if someone searched and agreed to buy seller's books
    
    def notify_seller(self, chat_id, seller_matching, book_available, contact_info, choice):
        bot.sendMessage(chat_id, 'Done! I have notified the seller. Please wait for the seller to contact you. You also can contact seller right now by using provided contact info')
        bot.sendMessage(chat_id, 'Thanks for using my service. I\'m always here. Please come back any time. See ya!')
        self._buy_or_not = False
        bot.sendMessage(seller_matching[choice], 'Hello my friend! Good news here! Someone wants to buy your book')
        bot.sendMessage(seller_matching[choice], 'Title: ' + str(book_available[choice]['title']   + '\n' + 'Author: ' + str(book_available[choice]['author']) + '\n'+ 'Condition: ' + str(book_available[choice]['condition']) + '% \n' + 'Price: ' + str(book_available[choice]['price']) + ' SGD \n' + 'Edition: ' + str(book_available[choice]['edition']) + '\n' + 'Year of Publication: ' + str(book_available[choice]['year of publication']) + '\n' + 'Publisher: ' + str(book_available[choice]['publisher']) + '\n' + 'Contact Infomation: ' + str(book_available[choice]['contact info']) + ' \n \n \n'))
        bot.sendMessage(seller_matching[choice], 'Contact of buyer: ' + str(contact_info))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Yes', callback_data='sell_book_yes')],
                            [InlineKeyboardButton(text='No', callback_data='sell_book_no')]])
        bot.sendMessage(chat_id, 'Do you wanna sell this book for buyer. Please contact the buyer for negotiation.' + '\n' + 'If your book is sold, please press Yes in order to remove book info from database. \n' + 'If you decide not to sell your book, please press No to keep it in database. \n', reply_markup=keyboard)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        key_words = ['books', 'book', 'second', 'hand', 'used',
                     'textbook', 'textbooks', 'buy', 'buying', 'sell',
                     'selling', 'seller', 'buyer', 'your job', 'who are you']
        flag = 0
        if content_type == 'text' and msg['text'] == '/cancel':
            self._old_msg = ''
            self._sell_info_flag = False
            self._buy_info_flag = False
            self._buy_or_not = False
            self._title_flag = False
            self._author_flag = False
            self._edition_flag = False
            self._year_flag = False
            self._publisher_flag = False
            self._price_flag = False
            self._condition_flag = False
            self._contact_flag = False
            self._continue_provide_info = True
            self._looking_for_title = '///'
            self._looking_for_author = '///'
            self._looking_for_contact = '///'
            self._contact = ''
            self._book_info = {}
            self._seller_matched_list = []
            for i in self._input_type_list:
                self._book_info[i] = ''
            
        if content_type == 'text' and self._sell_info_flag is False and msg['text'] == 'I want to sell second-hand books':
            self._sell_info_flag = True
            bot.sendMessage(chat_id, 'Awesome! I understand that you wanna sell books')
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Title'), KeyboardButton(text='Author')],
                [KeyboardButton(text='Edition'), KeyboardButton(text='Year of Publication')],
                [KeyboardButton(text='Publisher'), KeyboardButton(text='Condition in %')],
                [KeyboardButton(text='Price in SGD'), KeyboardButton(text='Contact Infomation')]], one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, 'Please click the tabs to provide information of your book', reply_markup=keyboard)
             
        if self._sell_info_flag is True:
            if self._continue_provide_info == True:

                if content_type == 'text' and msg['text'] == 'Title' and self._title_flag is False:
                    bot.sendMessage(chat_id, 'Yeah! Please provide an accurate title of the book. Thanks!')
                    self.get_input('title', content_type, chat_id, msg)
                    self._title_flag = True
                    
                if self._title_flag == True:
                    self.get_input('title', content_type, chat_id, msg)
                    
                if content_type == 'text' and msg['text'] == 'Author' and self._author_flag is False:
                    bot.sendMessage(chat_id, 'Let me know who is author of this book. Thanks!')
                    self.get_input('author', content_type, chat_id, msg)
                    self._author_flag = True
                    
                if self._author_flag == True:
                    self.get_input('author', content_type, chat_id, msg)
                    
                if content_type == 'text' and msg['text'] == 'Edition' and self._edition_flag is False:
                    bot.sendMessage(chat_id, 'What is edition of your book?')
                    self.get_input('edition', content_type, chat_id, msg)
                    self._edition_flag = True

                if self._edition_flag == True:
                    self.get_input('edition', content_type, chat_id, msg)

                if content_type == 'text' and msg['text'] == 'Year of Publication' and self._year_flag is False:
                    bot.sendMessage(chat_id, 'May I know the year of publication?')
                    self.get_input('year of publication', content_type, chat_id, msg)
                    self._year_flag = True

                if self._year_flag == True:
                    self.get_input('year of publication', content_type, chat_id, msg)

                if content_type == 'text' and msg['text'] == 'Publisher' and self._publisher_flag is False:
                    bot.sendMessage(chat_id, 'May I know name of publisher?')
                    self.get_input('publisher', content_type, chat_id, msg)
                    self._publisher_flag = True

                if self._publisher_flag == True:
                    self.get_input('publisher', content_type, chat_id, msg)

                if content_type == 'text' and msg['text'] == 'Price in SGD' and self._price_flag is False:
                    bot.sendMessage(chat_id, 'This infomation is really important. How much do you wanna sell your book? Please specify in SGD')
                    self.get_input('price', content_type, chat_id, msg)
                    self._price_flag = True

                if self._price_flag == True:
                    self.get_input('price', content_type, chat_id, msg)

                if content_type == 'text' and msg['text'] == 'Condition in %' and self._condition_flag is False:
                    bot.sendMessage(chat_id, 'Buyers really wanna know the condition of your book. Please provide it in %')
                    self.get_input('condition', content_type, chat_id, msg)
                    self._condition_flag = True
                    
                if self._condition_flag == True:
                    self.get_input('condition', content_type, chat_id, msg)

                if content_type == 'text' and msg['text'] == 'Contact Infomation' and self._contact_flag is False:
                    bot.sendMessage(chat_id, 'Buyers will need your contact info. Please provide your handphone number or email')
                    self.get_input('contact info', content_type, chat_id, msg)
                    self._contact_flag = True

                if self._contact_flag == True:
                    self.get_input('contact info', content_type, chat_id, msg)

        if content_type == 'text':
            if self._buy_info_flag is False and msg['text'] == 'I want to buy second-hand books':
                self._buy_info_flag = True
                bot.sendMessage(chat_id, 'Awesome! I understand that you wanna buy books')
                self._old_msg = msg['text']
    
        if self._buy_info_flag is True:
            if self._title_flag is False and self._looking_for_title == '///':
                bot.sendMessage(chat_id, 'Please tell me the title of book you are looking for')
                self._title_flag = True
            if self._title_flag is True and content_type != 'text' and msg['text'] != self._old_msg:
                bot.sendMessage(chat_id, 'Your input is not valid. Please type in correctly. Thanks')
            if self._title_flag is True and content_type == 'text' and msg['text'] != self._old_msg:
                bot.sendMessage(chat_id, 'Got it! Now, may I know who is the author of the book')
                self._looking_for_title = msg['text']
                self._title_flag = False
                self._old_msg = msg['text']
            if self._author_flag is False and self._title_flag is False and self._contact_flag is False:
                self._author_flag = True
            if self._author_flag is True and content_type != 'text' and msg['text'] != self._looking_for_title:
                bot.sendMessage(chat_id, 'Your input is not valid. Please type in correctly. Thanks')
            if self._author_flag is True and content_type == 'text' and msg['text'] != self._looking_for_title:
                bot.sendMessage(chat_id, 'Okay! Please provide contact number or email, so that the seller can contact you')
                self._looking_for_author = msg['text']
                self._author_flag = False
            if self._contact_flag is False and self._title_flag is False and self._author_flag is False:
                self._contact_flag = True
            if self._contact_flag is True and content_type != 'text' and msg['text'] != self._looking_for_author and msg['text'] != self._looking_for_title :
                bot.sendMessage(chat_id, 'Your input is not valid. Please type in correctly. Thanks')
            if self._contact_flag is True and content_type == 'text' and msg['text'] != self._looking_for_author and msg['text'] != self._looking_for_title:
                bot.sendMessage(chat_id, 'Yeah! Now, please wait for few seconds, I will come back for results')
                self._looking_for_contact = msg['text']
                self._contact = self._looking_for_contact
                self._contact_flag = False
            if self._looking_for_author != '///' and self._looking_for_title != '///' and self._looking_for_contact != '///':
                self.search(self._looking_for_title, self._looking_for_author, chat_id)
                self._looking_for_title = '///'
                self._looking_for_author = '///'
                self._looking_for_contact = '///'
                self._buy_info_flag = True
        if self._buy_or_not is True:
            if content_type == 'text':
                try:
                    choice = int(msg['text'])
                    if choice > len(self._seller_matched_list):
                        bot.sendMessage(chat_id, 'Your number is invalid. Please input the number no larger than ' + str(len(self._seller_matched_list)))
                    else:
                        self.notify_seller(chat_id, self._seller_matched_list, self._book_matched_list, self._contact, choice-1)
                        self._looking_for_contact = '///'
                except ValueError:
                    bot.sendMessage(chat_id, 'Please input a number corresponding to the book you want')
            else:
                bot.sendMessage(chat_id, 'Please input a number corresponding to the book you want')
                
        if self._sell_info_flag is False and self._buy_info_flag is False:
            for i in range(len(key_words)):
                if content_type == 'text' and key_words[i] in msg['text']:
                    flag = 1    	    
                    keyboard = ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text='I want to sell second-hand books')],
                        [KeyboardButton(text='I want to buy second-hand books')],
                        [KeyboardButton(text='No thanks')]], one_time_keyboard=True, resize_keyboard=True)
                    bot.sendMessage(chat_id, 'Hello my friend! Welcome to market platform for second-hand books. How can I help you?', reply_markup=keyboard)
                    ReplyKeyboardRemove(remove_keyboard=True)
                    break

        if flag == 0 and self._sell_info_flag is False and self._buy_info_flag is False and self._buy_or_not is False:
            bot.sendMessage(chat_id, smart_chat(msg['text']))
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='START', callback_data='start')]])
            bot.sendMessage(chat_id, 'Please click START button to begin', reply_markup=keyboard)
        if content_type == 'text':
            self._old_msg = msg['text']

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == 'start':
            keyboard = ReplyKeyboardMarkup(keyboard=[
                        [KeyboardButton(text='I want to sell second-hand books')],
                        [KeyboardButton(text='I want to buy second-hand books')],
                        [KeyboardButton(text='No thanks')]], one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(from_id, 'Hello my friend! Welcome to market platform for second-hand books. How can I help you?', reply_markup=keyboard)

        if query_data == 'No':
            book_store.book_info(from_id, self._book_info)
            self._book_info = {}
            for i in self._input_type_list:
                self._book_info[i] = ''
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Yes', callback_data='other_book_yes')],
                [InlineKeyboardButton(text='No', callback_data='other_book_no')]])
            bot.sendMessage(from_id, 'Sure. Do you have other book to sell?', reply_markup=keyboard)
        if query_data == 'Yes':
            self._continue_provide_info = True
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Title'), KeyboardButton(text='Author')],
                [KeyboardButton(text='Edition'), KeyboardButton(text='Year of Publication')],
                [KeyboardButton(text='Publisher'), KeyboardButton(text='Condition in %')],
                [KeyboardButton(text='Price in SGD'), KeyboardButton(text='Contact Infomation')]], one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(from_id, 'Yeah, Please continue input or change information  of your book', reply_markup=keyboard)
        if query_data == 'other_book_yes':
            keyboard = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Title'), KeyboardButton(text='Author')],
                [KeyboardButton(text='Edition'), KeyboardButton(text='Year of Publication')],
                [KeyboardButton(text='Publisher'), KeyboardButton(text='Condition in %')],
                [KeyboardButton(text='Price in SGD'), KeyboardButton(text='Contact Infomation')]], one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(from_id, 'Great, Please provide information of other book', reply_markup=keyboard)
            self._continue_provide_info = True
        if query_data == 'other_book_no':
            bot.sendMessage(from_id, 'Thank you so much. I will notify you when someone wants to buy your book. See ya!')
            self._sell_info_flag = False
            print(book_store._database)
        if query_data == 'search_other_book_no':
            bot.sendMessage(from_id, 'Thanks for using my service. I\'m always here. Please come back any time. See ya!')
            self._buy_info_flag = False
        if query_data == 'search_other_book_yes':
            bot.sendMessage(from_id, 'Okay! Please continue to search for other books')
            bot.sendMessage(from_id, 'Please tell me the title of book you are looking for')
            self._looking_for_title = ''
            self._looking_for_author = '///'
            self._title_flag = True
            self._buy_info_flag = True
        if query_data == 'buy_book_yes':
            bot.sendMessage(from_id, 'Which books do you want to buy? Please key in the number (like 1 for the first book in the list)')
            self._old_msg = ''
            self._buy_or_not = True
            self._buy_info_flag = False
        if query_data == 'buy_book_no':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Yes', callback_data='search_other_book_yes')],
                            [InlineKeyboardButton(text='No', callback_data='search_other_book_no')]])
            bot.sendMessage(from_id, 'Do you wanna search for other books', reply_markup=keyboard)
            


TOKEN = '430811551:AAEUJoN6B8hajtfHi2q9sz8gBYvlh3JjGuo'

bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(), create_open, ChatHandler, timeout=1000000000000000000), ])
bot.deleteWebhook()
MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)




