# -*- coding: utf-8 -*-
# specify pages from file
# specify regex from file
# if file non-existent, write. if existent append/update
# if update, large delay and concurrent req 1
# integrate mega
# generalize program for any site
# generalize element+field selection
# test if page is 404/not found
## write your own attributes for items and the value that gets filled into each?
## attr for each page:
### name string
### type string
### link string
### linktemplate string
### position (NOT update status) int
### last fetched page int
### dict of regexes to filter matched links against dict (save only matching)
### dict of regexes to filter matched links against dict (delete matching)
### last updated date-time DATE
###
## attr for each saved item:
### content
### fetched date
### fetched location
### does link go to a dead page?
# generalize field selection
## send non-mega to downloader?

### LAST:
#
# comments 72 lines
# document
# let user specify username/password from file
# log
# remove quotes

import scrapy
import re
from string import Template
from lossless.items import DownloadLink
from scrapy.exceptions import CloseSpider
import csv

class PagesSpider(scrapy.Spider):

    name = 'pages'
    start_urls = ['http://mylossless.3xforum.ro/login.php'] # let user specify login page
    close_manually = False

    tosaveregex = re.compile('mega\.nz|openload|drive\.google\.|zippyshare'
            '|girlshare|uptobox|turbobit|fisierulmeu|wetransfer|fileshare'
            '|we\.tl|easyupload|fileshare\.ro|uloz\.to|1fichier|sharebit'
            '|fisier\.ro|cloud\.mail\.ru|mediafire|yadi\.sh|tusfiles|flacmusic'
            '|blacksheepsound|ufile|depositfiles')

    toarchiveregex = re.compile('rutracker\.org|rock\.ru\/showthread|wordpress'
            '|itunes|tiny\.cc|skytorrents')

    def __init__(self, start=None, end=None, page=None, username=None,
            password=None, update=0, *args, **kwargs):

        super(PagesSpider, self).__init__(*args, **kwargs)
        self.start = int(start)
        self.end = int(end)
        self.page = page
        self.username = username
        self.password = password
        self.close_manually = False
        self.update = int(update)

        if self.update == 1:

            print('UPDATE MODE.')
            self.updatestate = {

                {'name': 'subforum', 'value': 0},
                {'name': 'recente', 'value': 0},
                {'name': 'cereri', 'value': 0},

                ]

        self.pages = { # make init_pages method to read from file and/or arguments and/or prompt

            'subforum': 
            { 'type': 'subforum', 
              'name': 'lossless3xforummainpage',

              'link': 'http://mylossless.3xforum.ro/topic/38/Muzica_Albume_in_'
                      'format_Lossless_FLAC_-_ROMANEASCA_/',

              'linktemplate': 'http://mylossless.3xforum.ro/topic/38/Muzica_'
                              'Albume_in_format_Lossless_FLAC_-_ROMANEASCA_/'
                              $page',
              'position': 0

            },

          'recente':       
          { 'type': 'topic', 
            'name': 'lossless3xforumrecente', 

            'link': 'http://mylossless.3xforum.ro/post/6798/$link/'
                    'Cele_mai_recente_melodii_in_format_LOSSLESS_/',

             'linktemplate': 'http://mylossless.3xforum.ro/post/6798/$link/'
                             'Cele_mai_recente_melodii_in_format_LOSSLESS_/',
             'position': 0
          },

          'cereri':
          { 'type': 'topic', 
            'name': 'lossless3xforumrecente', 

            'link': 'http://mylossless.3xforum.ro/post/6522/'
                    'CERERE_REQUEST_de_Albume_Melodii_in_format_FLAC_/',

            'linktemplate': 'http://mylossless.3xforum.ro/post/6522'
                            '/$link/CERERE_REQUEST_de_Albume_Melodii_in_'
                            'format_FLAC_/'
            'position': 0
          },

      }
                    

    def retrieve_last_page(self, page_to_retrieve): # ok

            response = scrapy.Request(url=page_to_retrieve['link'])

            if page_to_retrieve['type'] == 'subforum':
                
                last_page = int(response.css('table.punspacer>tr>td'
                                             '>a::text')[4].get())

            else if page_to_retrieve['type'] == 'topic':

                last_page = int(response.css('table.punspacer[cellspacing="1"]>'
                                             'tr>td>a::text')[3].get())

            return last_page

    #def parse_update_file(self, page, updatefile = 'updatestate.csv'): # generalize, let user specify updatefile, let user specify format
#
#        values = []
#
#        with open(updatefile, 'r') as f:
#            reader = csv.reader(f, newline='')
#            for row in reader:
#                values.append(row)
#
##        if type == 'main':
#            value = int(values[0].get('value'))
#            return value
#        elif type == 'recente':
#            value = int(values[1].get('value'))
#            return value
#        elif type == 'cereri':
#            value = int(values[2].get('value'))
#            return value
#
    def parse(self, response): # ok? maybe put all this into init function 

        # if -a `page` argument available in `pages` dict
        if self.page in self.pages:

            # if wanting to update this page. otherwise just get start
            # and end values from user

            if self.update == 1:
                # set the file-line from which to read the page's last 
                # scraped page
                position = self.pages[self.page]['position']
                # read that data and put it in the `updatestate` dict
                self.updatestate[position]['value'] = parse_update_file
                                                      (self.page)
                # set start value from dict value
                self.start = self.updatestate[position['value'] #
                # set end value from 
                self.end = self.retrieve_last_page(self.pages[self.page])

             # send
             return scrapy.FormRequest.from_response(response,
             formdata={'req_username':self.username,
                       'req_password':self.password}, 
                        callback=
                        self.construct_and_send_page_requests(self.start,           # START: retrieve last scraped page for this page from updatestate file
                                                            self.end,             # END retrieve last page of subforum/topic
                                                            self.pages[self.page] # the subforum/topic to scrape
                                                             ))
        else: 
            raise CloseSpider('page not available')

    def construct_and_send_page_requests(self,
                       start = 1, # self.start gets passed here(if update = 1, last scraped page of subforum/topic item)
                       end = 2, # self.end gets passed here (if update=1, last page of subforum/topic item)
                       page_to_retrieve_pages_from, # the subforum/topic to construct pages from
                       response):

        thearray = []
        s = Template(page_to_retrieve_pages_from['pagetemplate'])

        if self.update == 1: 
            # if topic and update, construct from newest page to oldest fetched page
            # in case its a subforum, doesn't matter
            for i in range(end,start):
                thearray.append(s.substitute(page=i)) 

        if start == end: 
            thearray.append(s.substitute(page=end)) # should 

        else:
            for i in range(start,end): 
                # most likely
                thearray.append(s.substitute(page=i)) 

            if page_to_retrieve_pages_from['type'] == 'subforum':
        for url in thearray():
                yield scrapy.Request(url=thearray,callback=self.construct_and_send_subforum_topics) 
            elif page_to_retrieve_pages_from['type'] == 'topic':
                yield scrapy.Request(url=thearray,callback=self.parse_topic_content)
        
    def construct_and_send_subforum_topics(self, response): #ok

        # select topic links
        selected_links = response.css('td.puncon2'
                                [style="word-break: break-word;'
                                'white-space: normal;"]>a::attr(href)').getall()

        for link in selected_links:
            newreq = response.urljoin(link)
            # send topic to parse_topic_content and continue loop
            yield scrapy.Request(url=newreq, callback=self.parse_topic_content)  

    def parse_topic_content(self, response): # ok

        if self.update == 1:
            # reverse so as to get newest posts from a page first
            selected = response.css('table.punplain>tr>td>'
                    'span.puntext>a').getall().reverse() 
        else:
            selected = response.css('table.punplain>tr>td>'
                    'span.puntext>a').getall()

        for link in selected:
#           if self.close_manually == True and self-update == 1:
#               raise CloseSpider(reason='got an update-ending duplicate. '
                                         'means its up-to-date. closing '
                                         'spider. Bye Bye.') 

            #print('at for actuallink = %s\n' % link)
            parsed_link = self.parse_link(link)
            item = self.check_link(parsed_link) 
            # send to item pipeline and continue !
            yield item
                
    def check_link(self, link):

        # if link matches any of the strings in tosave/toarchive regex,
        # it's a good link and return it. otherwise don't return anything
        if self.tosaveregex.search(link): # if its a good d/l link

            dl = DownloadLink(url=link,type='tosave')

            #print('VALID LINK FOUND AT TOSAVEREGEX POINT IN PARSEPOSTS %s\n' 
                    % link)

            #print(dl)
            return dl
    
        elif self.toarchiveregex.search(link):
    
            dl = DownloadLink(url=str(link),type='tosave')

            #print('VALID LINK FOUND AT TOARCHIVEREGEX POINT IN PARSEPOSTS %s\n' 
                    % link)

            #print(dl)
            return dl

    def parse_link(self, link):

        # if link leads to redirect page
        if link.find('...') > 0:
            # strip redir link from elem
            #print('link has ... %s\n' % link)
            link = re.sub('<a href="','',link) 
            link = re.sub('".*','',link)
            # make absolute url of redir link
            link = response.urljoin(link) # make redir link
            link = re.sub('==','=%3D',link)

            # go to redirect page to fetch response w/ full link
            redir_response = scrapy.Request(url=link) 
            # parse real full link from redirect page response
            link = redir_response.css('td.puncon1>a::attr(href)').get() 
            #print('link at find ... after sub is %s\n' % link)

        # if link doesn't lead to redirect page
        else:
            # strip full ink from elem
            link = re.sub('<a href=.*>h','h',link)
            link = re.sub('</a>','',link)
            link = re.sub('"','',link)
            #print('at else point find point %s\n' % link)

        return link
