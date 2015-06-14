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
        max_links = 10
        links = links_query.fetch(max_links)

        error = self.request.get('error',"")

        template_values = {
            'links': links,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'error': error,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(**template_values))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        # The "post" is to store the information in the datastore
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        link = Link(parent=guestbook_key(guestbook_name))

        user_name = self.request.get('name')
        user_url = self.request.get('linkurl')
        min_name = 5
        # the name of the link must be at least 5 characters
        min_url = 8
        # the ulr must be at least 8 characters

        if len(user_name) < min_name or len(user_url) < min_url:
            error = "Please enter a site description and a valid URL."

            query_params = {'guestbook_name': guestbook_name,
                            'error': error}
            self.redirect('/?' + urllib.urlencode(query_params) + '#bottom')

        else:
            link.name = user_name
            link.linkurl = user_url
            error = "Thanks!"
            link.put()

            query_params = {'guestbook_name': guestbook_name,
                            'error': error}
            self.redirect('/?' + urllib.urlencode(query_params) + '#bottom')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)