# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from flask import Flask, render_template, request, jsonify, json
from bs4 import BeautifulSoup
import urllib2
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback
import requests


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.searchbox.html')



@app.route("/log")
def logTest():
    app.logger.warning('testing warning log')
    app.logger.error('testing error log')
    app.logger.info('testing info log')
    return "Code Handbook !! Log testing."


@app.errorhandler(Exception)
def exceptions(e):
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                 ts,
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 tb)
    return "Internal Server Error", 500


@app.after_request
def after_request(response):
    # This IF avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.info('%s %s %s %s %s %s',
                    ts,
                    request.remote_addr,
                    request.method,
                    request.scheme,
                    request.full_path,
                    response.status)
    return response


@app.route('/', methods=['POST'])
def executeSearch():

    site = request.form['searchtext']
    print 'Site entered is {}'.format(site)

    head1 = []
    head2 = []

    checkMobileFriendly = 'https://www.googleapis.com/pagespeedonline/v3beta1/mobileReady?url=' + site


    print '***checkMobileFriendly string {}***'.format(checkMobileFriendly)

    try:
        r = requests.head(site)
        status_code = r.status_code
        print 'Connecting to {} ......'.format(site)
        print 'status code is {}....'.format(r.status_code)
        if r.status_code != 401 or r.status_code != 404 or r.status_code != 503:
            print 'Connected to {} with status code of {}'.format(site, r.status_code)
            page = urllib2.urlopen(site).read()
            soup = BeautifulSoup(page, 'html.parser')
            print('****STATUS CODE*** {}').format(r.status_code)

            title = soup.title.string


            desc_meta = soup.findAll(attrs={"name": "description"})

            if len(desc_meta) > 0:

                descriptionString = desc_meta[0]['content'].encode('utf-8')
                descriptionLength = len(descriptionString)
                print 'description of page is {}'.format(descriptionString)
                print 'length of description is {}'.format(descriptionLength)

            else:
                print 'Description is empty'

            r = requests.get(checkMobileFriendly)

            data = r.json()
            mobileFriendly = data.get('ruleGroups').get('USABILITY').get('pass')

            mobileFriendlyScore = data.get('ruleGroups').get('USABILITY').get('score')

            print ' Is site Mobile friendly? {}'.format(mobileFriendly)

            print 'What if the mobile friendly score {}'.format(mobileFriendlyScore)

            print 'Domain' + '--> ' + site

            print 'Title' + '-->' + title

            print 'Title word count is', len(title)

            h1 = soup.find_all('h1')

            h2 = soup.find_all('h2')

            for h in h1:

                head1.append(h.get_text())

            for h in h2:
                head2.append(h.get_text())


            #return json.dumps({'targetSite': site, 'responseCode': status_code,'title': title, 'titleLength': len(title),'ismobile': mobileFriendly, 'siteScore': mobileFriendlyScore, 'h1': head1, 'h2': head2})

            return json.dumps(
                {'targetSite': site, 'responseCode': status_code, 'title': title, 'titleLength': len(title),
                 'ismobile': mobileFriendly, 'siteScore': mobileFriendlyScore})
    except requests.ConnectionError:
        print("failed to connect")
        return 'failure'


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    handler = RotatingFileHandler('request.log', maxBytes=10000, backupCount=3)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=3)
    logger = logging.getLogger('__name__')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    app.run(host='127.0.0.1', port=82)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
