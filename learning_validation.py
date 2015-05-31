import cgi 
import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#The Jinja template allows for creation of HTML code without having to repeat HTML

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
# I set a parent key on the 'Links' to ensure that they are all
# in the same entity group. The data type is a string, and 'Links'
# is my only entity group.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    return ndb.Key('Guestbook', guestbook_name)

# It is not likely that a valid site name is less than 5 characters, so I'm inserting a check to verify that the user input at least 5 characters
def valid_name(name):
    if len(name) > 5:
        return name

# It is not likely that a valid url is less than 8 characters, so I'm inserting a check to verify that the user input at least 8 characters 
def valid_url(linkurl):
    if len(linkurl) > 8:
        return linkurl

    #creating an object class, Link, to store each website link entry

class Link(ndb.Model):
    """A main model for representing an individual website link entry."""
    name = ndb.StringProperty(indexed=False)
    linkurl = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

# The MainPage Request handler defines the query that is used to
# return the links that have been stored in the Link datastore.

class MainPage(webapp2.RequestHandler):
    def get(self):
        # The "get" is to 'pull' information from the datastore
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        links_query = Link.query(
            ancestor=guestbook_key(guestbook_name)).order(-Link.date)
        links = links_query.fetch(15)


        template_values = {
            'links': links,
            'guestbook_name': urllib.quote_plus(guestbook_name),
        }
       
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(**template_values))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        # The "post" is to store the information in the datastore
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        link = Link(parent=guestbook_key(guestbook_name))

        user_name = valid_name(self.request.get('name'))
        user_url = valid_url(self.request.get('linkurl'))

        if not (user_name and user_url):
            self.response.out(template)
        else:
            link.name = self.request.get('user_name')
            link.linkurl = self.request.get('user_url')
            link.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)