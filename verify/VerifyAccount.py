url = raw_input('Enter MFC Verification URL: ')

def Verify_Account (url):
        global gpasscode
        global guser
        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(  urllib2.HTTPRedirectHandler(),
                                        urllib2.HTTPHandler(debuglevel=0),
                                        urllib2.HTTPSHandler(debuglevel=0),
                                        urllib2.HTTPCookieProcessor(cookies))
        response = opener.open(url)
        http_headers = response.info()
        cookie = Cookie.SimpleCookie()
        try:
                cookie.load(http_headers['set-cookie'])
                User=cookie['username'].value
                Passcode = cookie['passcode'].value
                UID=cookie['user_id'].value
        except KeyError:
                return
        print ("Account Verified for user %s and received passcode %s user id %s\n"
                % ( User, Passcode, UID))
        guser=User
        gpasscode=Passcode
        print ("You can connect to the room ..")