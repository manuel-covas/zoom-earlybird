import os
import time
import psutil
import subprocess

import requests
import http
import html
import json


config_file = open("config.json", "r")
config = json.decoder.JSONDecoder().decode(config_file.read())
config_file.close()

try:
    zoom_path = config.zoom_path
    identity_provider = config.identity_provider
    username = config.username
    password = config.password
except:
    print("Failed to load configuration from config.json")
    exit(0)


# Identity Providers:

# Universidades
# https://idp.iscte-iul.pt/idp/shibboleth                  [SUPPORTED] ISCTE-IUL - Instituto Universitario de Lisboa
# https://idprovider.uab.pt/idp/shibboleth                 [UNKNOWN]   Universidade Aberta
# https://idp.ual.pt/idp/shibboleth                        [UNKNOWN]   Universidade Aut&oacute;noma de Lisboa
# https://wayf.ucp.pt                                      [UNKNOWN]   Universidade Cat&oacute;lica Portuguesa
# https://idp.ubi.pt/idp/shibboleth                        [UNKNOWN]   Universidade da Beira Interior
# https://idp2.uma.pt/idp/shibboleth                       [UNKNOWN]   Universidade da Madeira
# https://idp.ua.pt/idp/shibboleth                         [UNKNOWN]   Universidade de Aveiro
# https://idp.uc.pt/idp/shibboleth                         [UNKNOWN]   Universidade de Coimbra
# https://aai.uevora.pt/idp/shibboleth                     [UNKNOWN]   Universidade de &Eacute;vora
# https://id.fc.ul.pt/simplesaml/saml2/idp/metadata.php    [UNKNOWN]   ULisboa - Faculdade de Ciências
# https://aai.isa.utl.pt/simplesaml/saml2/idp/metadata.php [UNKNOWN]   ULisboa - Instituto Superior de Agronomia
# https://idp.iseg.ulisboa.pt/idp/shibboleth               [UNKNOWN]   ULisboa - Instituto Superior de Economia e Gestão
# https://id.tecnico.ulisboa.pt/saml                       [UNKNOWN]   ULisboa - Instituto Superior Técnico
# https://wayf.ulisboa.pt                                  [UNKNOWN]   Universidade de Lisboa
# https://idp.utad.pt/idp/shibboleth                       [UNKNOWN]   Universidade de Tr&aacute;s os Montes e Alto Douro
# https://si-saai.ualg.pt/idp/shibboleth                   [UNKNOWN]   Universidade do Algarve
# https://idp.uminho.pt/idp/shibboleth                     [UNKNOWN]   Universidade do Minho
# https://wayf.up.pt/idp/shibboleth                        [UNKNOWN]   Universidade do Porto
# https://login.uac.pt/idp/shibboleth                      [UNKNOWN]   Universidade dos A&ccedil;ores
# https://idp.universidadeeuropeia.pt/idp/shibboleth       [UNKNOWN]   Universidade Europeia
# https://idp.ufp.pt/idp/shibboleth                        [UNKNOWN]   Universidade Fernando Pessoa
# https://idp.lis.ulusiada.pt/idp/shibboleth               [UNKNOWN]   Universidade Lus&iacute;ada
# https://aai.ulusofona.pt/idp/shibboleth                  [UNKNOWN]   Universidade Lus&oacute;fona
# https://idp.ulp.pt/idp/shibboleth                        [UNKNOWN]   Universidade Lus&oacute;fona do Porto
# https://wayf.unl.pt/wayf/"                               [UNKNOWN]   Universidade Nova de Lisboa
# https://idp.uportu.pt/idp/shibboleth                     [UNKNOWN]   Universidade Portucalense

# Politécnicos
# https://idp.ipluso.pt/idp/shibboleth                     [UNKNOWN]   Instituto Politécnico da Lusófonia
# https://idp.ipbeja.pt/idp/shibboleth                     [UNKNOWN]   Instituto Polit&eacute;cnico de Beja
# https://idp.ipb.pt/idp/shibboleth                        [UNKNOWN]   Instituto Polit&eacute;cnico de Bragan&ccedil;a
# https://idp00.ipcb.pt/simplesaml/saml2/idp/metadata.php  [UNKNOWN]   Instituto Polit&eacute;cnico de Castelo Branco
# https://wayf.ipc.pt/IPCds                                [UNKNOWN]   Instituto Polit&eacute;cnico de Coimbra
# https://idp.ipg.pt/idp/shibboleth                        [UNKNOWN]   Instituto Polit&eacute;cnico da Guarda
# https://idp.ipleiria.pt/idp/shibboleth                   [UNKNOWN]   Instituto Polit&eacute;cnico de Leiria
# https://idp.net.ipl.pt/simplesaml/saml2/idp/metadata.php [UNKNOWN]   Instituto Polit&eacute;cnico de Lisboa
# https://idp.ipportalegre.pt/idp/shibboleth               [UNKNOWN]   Instituto Polit&eacute;cnico de Portalegre
# https://vrctsaai.ipsantarem.pt/idp/shibboleth            [UNKNOWN]   Instituto Polit&eacute;cnico de Santar&eacute;m
# https://idp.ips.pt/idp/shibboleth                        [UNKNOWN]   Instituto Polit&eacute;cnico de Set&uacute;bal
# https://idp.ipt.pt/idp/shibboleth                        [UNKNOWN]   Instituto Polit&eacute;cnico de Tomar
# https://idp.ipvc.pt/idp/shibboleth                       [UNKNOWN]   Instituto Polit&eacute;cnico de Viana do Castelo
# https://wayf.ipv.pt/IPVds                                [UNKNOWN]   Instituto Polit&eacute;cnico de Viseu
# https://idp.ipca.pt/idp/shibboleth                       [UNKNOWN]   Instituto Polit&eacute;cnico do C&aacute;vado e do Ave
# https://idp01.net.ipp.pt/idp/shibboleth                  [UNKNOWN]   Instituto Polit&eacute;cnico do Porto
# https://idp.iseclisboa.pt/idp/shibboleth                 [UNKNOWN]   ISEC Lisboa - Instituto Superior de Educação e Ciências
# https://idp.ispa.pt/idp/shibboleth                       [UNKNOWN]   ISPA - Instituto Universitário de Ciências Psicológicas

# Escolas de Ensino Superior
# https://idpesenfc.esenfc.pt/idp/shibboleth               [UNKNOWN]   Escola Superior de Enfermagem de Coimbra
# https://esel-idp02.esel.pt/idp/shibboleth                [UNKNOWN]   Escola Superior de Enfermagem de Lisboa
# https://idp.esenf.pt/idp/shibboleth                      [UNKNOWN]   Escola Superior de Enfermagem do Porto
# https://idp.eshte.pt/idp/shibboleth                      [UNKNOWN]   Escola Superior de Hotelaria e Turismo do Estoril
# https://idp.enautica.pt/idp/shibboleth                   [UNKNOWN]   Escola Superior Náutica Infante Dom Henrique

# Outras
# https://conferencia.exercito.pt/idp/shibboleth           [UNKNOWN]   Academia Militar
# https://lxidp01.ani.pt/idp/shibboleth                    [UNKNOWN]   Agência Nacional de Inova&ccedil;&atilde;o
# https://idp.apambiente.pt/idp/shibboleth                 [UNKNOWN]   Agência Portuguesa do Ambiente
# https://srvidm01.cccm.pt/idp/shibboleth                  [UNKNOWN]   Centro Científico e Cultural de Macau
# https://idp.cienciaviva.pt/idp/shibboleth                [UNKNOWN]   Ciencia Viva
# https://idp.cespu.pt/idp/shibboleth                      [UNKNOWN]   CESPU - Cooperativa de Ensino Superior Polit&eacute;cnico e Universit&aacute;rio
# https://idp.ciimar.up.pt/idp/shibboleth                  [UNKNOWN]   CIIMAR
# https://idpguest.fccn.pt/idp/shibboleth                  [UNKNOWN]   Convidados FCCN
# https://idp.dges.gov.pt/idp/shibboleth                   [UNKNOWN]   Dire&ccedil;&atilde;o Geral do Ensino Superior
# https://idp.dgterritorio.pt/idp/shibboleth               [UNKNOWN]   Direção Geral do Território
# https://idp1-escnaval.marinha.pt/idp/shibboleth          [UNKNOWN]   Escola Naval
# https://idp.fccn.pt/idp/shibboleth                       [UNKNOWN]   FCCN - unidade da FCT I.P.
# https://idp.fct.pt/idp/shibboleth                        [UNKNOWN]   FCT - Funda&ccedil;&atilde;o para a Ciencia e a Tecnologia
# https://idp.iave.pt/idp/shibboleth                       [UNKNOWN]   Instituto de Avaliação Educativa
# https://idp.inesctec.pt/idp/shibboleth                   [UNKNOWN]   Instituto de Engenharia de Sistemas e Computadores Tecnologia e Ciencia - INESC TEC
# https://idp.igc.gulbenkian.pt/idp/shibboleth             [UNKNOWN]   Instituto Gulbenkian de Ciência
# https://idp.hidrografico.pt/idp/shibboleth               [UNKNOWN]   Instituto Hidrográfico
# https://idp.ipdj.gov.pt/idp/shibboleth                   [UNKNOWN]   Instituto Português do Desporto e Juventude
# https://idp.ipma.pt/idp/shibboleth                       [UNKNOWN]   Instituto Português do Mar e da Atmosfera
# https://idp.ium.pt/idp/shibboleth                        [UNKNOWN]   Instituto Universitário Militar
# https://idp.inl.int/idp/shibboleth                       [UNKNOWN]   INL - International Iberian Nanotechnology Laboratory
# https://idp.lip.pt/idp/shibboleth                        [UNKNOWN]   Laborat&oacute;rio de Instrumenta&ccedil;&atilde;o e F&iacute;sica Experimental de Particulas - LIP
# https://idp.lnec.pt/idp/shibboleth                       [UNKNOWN]   Laboratorio Nacional de Engenharia Civil
# https://lnegrctsaai.lneg.pt/idp/shibboleth               [UNKNOWN]   Laboratorio Nacional de Energia e Geologia
# https://idp.sec-geral.mec.pt/idp/shibboleth              [UNKNOWN]   Secretaria Geral da Educa&ccedil;&atilde;o e Ci&ecirc;ncia


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
        exit(0)

def search_and_terminate():
    for pid in psutil.pids():
        
        try:
            process = psutil.Process(pid)
            path = process.cmdline()[0].lower()
        except:
            continue

        if path.count("zoom.exe") > 0 or path.count("zoom-client") or path.count("bin\\zoom") > 0 or path.count("bin/zoom") > 0:
            process.terminate()



# Login SSO
print("Running SSO Login flow...")

session = requests.Session() # Gotta carry the cookies around


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

req3 = session.post(req3_url, [("user_idp", identity_provider), ("Selected", "Entrar")])
check_response(req3)

req4_url = req3.text.split('<form method="post" action="')[1].split('">')[0]
saml_request = req3.text.split('<input type="hidden" name="SAMLRequest" value="')[1].split('"')[0]


print("Passing SAMLRequest to "+req4_url)

req4 = session.post(req4_url, [("SAMLRequest", saml_request)])
check_response(req4)

req5_url_path = req4.text.split('<form id="loginForm" action="')[1].split('"')[0]
req5_url = req4.url


print("Logging in at "+req5_url)

req5 = session.post(req5_url, [("j_username", username), ("j_password", password), ("_eventId_proceed", "")])
check_response(req5)

try:
    req6_url = html.unescape(req5.text.split('<form action="')[1].split('"')[0])
    saml_response = req5.text.split('name="SAMLResponse" value="')[1].split('"')[0]
except:
    print("\nFailed to extract SAMLResponse from the HTML returned by:\n"+req5_url)
    print(  "Most likely a failed login!")
    exit(0)

print("Passing SAMLResponse to "+req6_url)

req6 = session.post(req6_url, [("SAMLResponse", saml_response)])
check_response(req6)

req7_url = req6.text.split('<form method="post" action="')[1].split('"')[0]
saml_response = req6.text.split('name="SAMLResponse" value="')[1].split('"')[0]


print("Submitting SAMLResponse to "+req7_url+" with Firefox's User-Agent Header (Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0)")

req7 = session.post(req7_url, [("SAMLResponse", saml_response)])
check_response(req7)

temp = req7.text.split('" id="sso-button"')[0].split('href="')
zoom_desktop_sso_link = temp[len(temp) - 1]


print("\nSUCCESSFUL SSO LOGIN.\nPassing to desktop client: "+zoom_desktop_sso_link)
subprocess.Popen([zoom_path, "--url="+zoom_desktop_sso_link])

