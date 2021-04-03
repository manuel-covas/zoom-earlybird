import subprocess
import requests
import http
import html


# Disable Diffie-Hellman key exchange for https://wayf.fccn.pt (Host's Diffie-Hellman Exchange key is vulnerable to Logjam Attack - https://weakdh.org/)

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context

class NoDiffieHellmanAdapter(HTTPAdapter):
    """
    A TransportAdapter that disables DiffieHellman support in Requests.
    """
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="HIGH:!DH:!aNULL")
        kwargs['ssl_context'] = context
        return super(NoDiffieHellmanAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers="HIGH:!DH:!aNULL")
        kwargs['ssl_context'] = context
        return super(NoDiffieHellmanAdapter, self).proxy_manager_for(*args, **kwargs)


# Check HTTP responses for errors and log them

def check_response(request):
    print(str(request.status_code) +" - "+ http.client.responses[request.status_code])
    if request.status_code != 200:
        error_message = (time.asctime()+"\n"+
                         "HTTP request did not succeed.\n"+
                         "{0} {1}\n"+
                         "Response: {2} - {3}\n\n").format(request.request.method, request.url, request.status_code, http.client.responses[request.status_code])
        f = open("error_logs.txt", "a")
        f.write(error_message)
        f.close()
        raise Exception(error_message)


# Current login flow is for https://idp.iscte-iul.pt/idp/shibboleth only, might work for others.

def sso_login(config):

    if len(config["identity_provider"]) < 5:
        raise Exception("Not using SSO login. (identity_provider URL too short)")


    # Persist cookies
    session = requests.Session()
    # Apply no Diffie-Hellman adapter
    session.mount("https://wayf.fccn.pt", NoDiffieHellmanAdapter())


    print("Running SSO Login flow...")
    print("Getting SAML from https://videoconf-colibri.zoom.us/saml/login?from=desktop...")

    req1 = session.get("https://videoconf-colibri.zoom.us/saml/login?from=desktop")
    check_response(req1)

    saml_request = req1.text.split('<input type="hidden" name="SAMLRequest" value="')[1].split('"/>')[0]


    print("Passing SAMLRequest to https://webconf-colibri.fccn.pt/simplesaml/saml2/idp/SSOService.php...")

    req2 = session.post("https://webconf-colibri.fccn.pt/simplesaml/saml2/idp/SSOService.php", [("SAMLRequest", saml_request)])
    check_response(req2)

    req3_url_path = html.unescape(req2.text.split('<form id="IdPList" name="IdPList" method="post" onSubmit="return checkForm()" action="')[1].split('" >')[0])
    req3_url = "https://wayf.fccn.pt" + req3_url_path


    print("Submitting identity provider to "+req3_url.split("?")[0])

    req3 = session.post(req3_url, [("user_idp", config["identity_provider"]), ("Selected", "Entrar")])
    check_response(req3)

    req4_url = req3.text.split('<form method="post" action="')[1].split('">')[0]
    saml_request = req3.text.split('<input type="hidden" name="SAMLRequest" value="')[1].split('"')[0]


    print("Passing SAMLRequest to "+req4_url)

    req4 = session.post(req4_url, [("SAMLRequest", saml_request)])
    check_response(req4)

    req5_url_path = req4.text.split('<form id="loginForm" action="')[1].split('"')[0]
    req5_url = req4.url


    print("Logging in at "+req5_url)

    req5 = session.post(req5_url, [("j_username", config["username"]), ("j_password", config["password"]), ("_eventId_proceed", "")])
    check_response(req5)

    try:
        req6_url = html.unescape(req5.text.split('<form action="')[1].split('"')[0])
        saml_response = req5.text.split('name="SAMLResponse" value="')[1].split('"')[0]
    except:
        print("\nFailed to extract SAMLResponse from the HTML returned by:\n"+req5_url)
        print(  "Most likely a failed login!")
        raise Exception("\nFailed to extract SAMLResponse from the HTML returned by:\n"+
                        req5_url+
                        "\nMost likely a failed login!")

    print("Passing SAMLResponse to "+req6_url)

    req6 = session.post(req6_url, [("SAMLResponse", saml_response)])
    check_response(req6)

    req7_url = req6.text.split('<form method="post" action="')[1].split('"')[0]
    saml_response = req6.text.split('name="SAMLResponse" value="')[1].split('"')[0]


    print("Submitting SAMLResponse to "+req7_url+" with Firefox's User-Agent Header (Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0)")

    req7 = session.post(req7_url, [("SAMLResponse", saml_response)], headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"})
    check_response(req7)
    

    temp = req7.text.split('" id="sso-button"')[0].split('href="')
    zoom_desktop_sso_link = temp[len(temp) - 1]


    print("\nSuccessful SSO Login.")
    return zoom_desktop_sso_link