# importing the requests library
import requests
from pprint import pprint
import random
import json
# api-endpoint
URLS = {"mediator" : "http://localhost:8000/api/v1/",
        'guardian' : "http://localhost:8001/api/v1/"
}

from electionguard.ballot import PlaintextBallot
def ping(api_name):

    try:
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {}

        ping_url = URLS[api_name] + "ping"

        # sending get request and saving the response as response object
        r = requests.get(url = ping_url, params = PARAMS)

        # extracting data in json format
        data = r.json()

        if data == "pong":
            return True
        else:
            return False
    except Exception as e:
        return False

def get_election_constants():
    params = {}

    election_constants_url = URLS["mediator"] + "election/constants"

    # sending get request and saving the response as response object
    r = requests.get(url = election_constants_url, params = params)

    # extracting data in json format

    data = r.json()

    print(data)

    result = {}
    result["g"] = int(data["generator"])
    result["p"] = int(data["large_prime"])
    result["q"] = int(data["small_prime"])
    result["k"] = int(data["cofactor"])

    assert (result["k"] * result["q"]) + 1 == result["p"] 

    return result

def create_guardian(guardian_id, nonce, sequence_order="1", guardians_count="1", quorum="1"):

    # params = '{'+params +'}'
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    create_guardian_url = URLS["guardian"] + "guardian"

    f = open ('guard/aux_key.json', "r")
    aux = json.loads(f.read())
    f.close()
    params = {"quorum": quorum, "nonce":nonce, "id": guardian_id, "number_of_guardians": guardians_count, "sequence_order":sequence_order, "auxiliary_key_pair": aux}

    # sending get request and saving the response as response object
    r = requests.post(url = create_guardian_url, json=params, headers=headers)
    data = r.json()

    pprint(data)

def generate_guardian_election_key(nonce, count=1):
    params = {"quorum": 1, "nonce":nonce}

    generate_key_url = URLS["guardian"] + "key/election/generate"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    # sending get request and saving the response as response object
    r = requests.post(url = generate_key_url, json = params, headers=headers)

    print(r.json())
# def create_guardians(nonce, count=1):

def modexp( base, exp, modulus ):
    return pow(base, exp, modulus)

def generate_private_key(q):
    r = random.getrandbits(256)
    return (r % (q - 2)) + 2;

def generate_keypair(p, q, g):
    # x = generate_private_key(q)
    x= 1234
    y = modexp(g, x,p)

    return (x,y)

def create_context():
    create_context_url = URLS["mediator"] + "election/context"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    f = open ('manifest.json', "r")
     
    # Reading from file
    manifest = json.loads(f.read())
        
    # Closing file
    f.close()
    data = {
      "description": manifest,
      "elgamal_public_key": "198334824120421388904216865242201487863049506799659317408064571058156011271089085492198379812867947386637462314227469914893143411915951250722331805706283232952061910334148828985410033737536941007853790575367251939419686748807052761934205381975550044078577342670958241701264969156497549252352731440749094502414999195890057531492578689364066823872794251281278788024915798547281197605605627537808806149923381719918880230729037722889556147390830608464703259214299327977134732075814978542781235381593406974240025232563371020635860564981245096819967247058905460555301962407068931631592449538300161889770040149943014713374915337618418340382208636129194747939316599536387330644764006607495634724926987669094067772990180216481132047130780106953387768379056264618945001593722606290638392403674790909092631446939341202633556247578645136757830370416646724095631976498263933798268842029858711442586668894509301603395158670257187332377999243388873846314344604196006714734595778048154551187530855845560571585862715902395000887950879720663535818019943949216856295440711476797010371525655060904398239060242867490422752062349040426236557745047158699975264065809709840724672275957889433526645001008628354496094468273607358457038608077285467067496984063",
      "number_of_guardians": 1,
      "quorum": 1,
      "commitment_hash": "3BD428B97477F8B29CF4052D5E86D032AE20B3FFEA72B9A5FB36BCC98A55D5DA"
    }

    r = requests.post(url = create_context_url, json = data)

    print(r.json())

# def validate_manifest():


def create_election_keys():
    print("create election keys: NOT IMPLEMENTED")

def mediator_validate_manifest():

    validate_manifest_url = URLS["mediator"] + "election/validate/description"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}
    f = open ('manifest.json', "r")
     
    # Reading from file
    manifest = json.loads(f.read())
        
    # Closing file
    f.close()

    params = {"manifest": manifest}
    # sending get request and saving the response as response object
    r = requests.post(url = validate_manifest_url, json = params, headers=headers)

    print(r.json())

def mediator_combine_election_keys():

    combine_keys_url = URLS["mediator"] + "key/election/combine"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    params = {"election_public_keys": ['198334824120421388904216865242201487863049506799659317408064571058156011271089085492198379812867947386637462314227469914893143411915951250722331805706283232952061910334148828985410033737536941007853790575367251939419686748807052761934205381975550044078577342670958241701264969156497549252352731440749094502414999195890057531492578689364066823872794251281278788024915798547281197605605627537808806149923381719918880230729037722889556147390830608464703259214299327977134732075814978542781235381593406974240025232563371020635860564981245096819967247058905460555301962407068931631592449538300161889770040149943014713374915337618418340382208636129194747939316599536387330644764006607495634724926987669094067772990180216481132047130780106953387768379056264618945001593722606290638392403674790909092631446939341202633556247578645136757830370416646724095631976498263933798268842029858711442586668894509301603395158670257187332377999243388873846314344604196006714734595778048154551187530855845560571585862715902395000887950879720663535818019943949216856295440711476797010371525655060904398239060242867490422752062349040426236557745047158699975264065809709840724672275957889433526645001008628354496094468273607358457038608077285467067496984063']}
    # sending get request and saving the response as response object
    r = requests.post(url = combine_keys_url, json = params, headers=headers)

    print(r.json())

def cast_ballot():
    cast_ballot_url = URLS["mediator"] + "ballot/cast"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    f = open ('manifest.json', "r")
    manifest = json.loads(f.read())
    f.close()

    f = open ('against_ballot.json', "r")
    ballot = PlaintextBallot(json.loads(f.read()))
    f.close()
    data = {
      'ballot': ballot,
      'description': manifest,
      'context': {'crypto_base_hash': '93751301913348147876791859490184215718852025451734709618776164122389040060514', 'crypto_extended_base_hash': '3449977982734458371285042392739795262122053997766049762108451437137013153037', 'description_hash': '77420478244482842663652152894500149996445529618297048950885244207625545100955', 'elgamal_public_key': '16971526958896742104429768272942978154150377497253512678568819011256388968655', 'number_of_guardians': 1, 'quorum': 1}
      }

    r = requests.post(url = cast_ballot_url, json = data, headers=headers)

    print(r.json())

def encrypt_ballot():
    encrypt_ballot_url = URLS["mediator"] + "ballot/encrypt"
    headers = {'Content-Type': 'application/json', "accept": "application/json"}

    f = open ('manifest.json', "r")
    manifest = json.loads(f.read())
    f.close()

    f = open ('against_ballot.json', "r")
    ballot = json.loads(f.read())
    print(ballot)
    f.close()
    data = {
          "ballots": [
            ballot
          ],
          "seed_hash": "110191403412906482859082647039385908787148325839889522238592336039604240167009",
          "nonce": "110191403412906482859082647039385908787148325839889522238592336039604240167009",
          "description": manifest,
          'context': {'crypto_base_hash': '93751301913348147876791859490184215718852025451734709618776164122389040060514', 'crypto_extended_base_hash': '3449977982734458371285042392739795262122053997766049762108451437137013153037', 'description_hash': '77420478244482842663652152894500149996445529618297048950885244207625545100955', 'elgamal_public_key': '16971526958896742104429768272942978154150377497253512678568819011256388968655', 'number_of_guardians': 1, 'quorum': 1}
      }

    pprint(data)
    r = requests.post(url = encrypt_ballot_url, json = data, headers=headers)

    # print(r.json())

    print(r.text)

print(f'Testing Mediator API connection: {ping("mediator")}')
print(f'Testing Guardian API connection: {ping("guardian")}')

create_guardian("testGuardian", "1234")
# generate_guardian_key("1234")
# generate_guardian_election_key("1234")
mediator_combine_election_keys()
# mediator_validate_manifest()

# print("Election constants")
# pprint(constants)
# print(generate_keypair(p, q, g))
create_context()
constants = get_election_constants()
# encrypt_ballot()
# cast_ballot()
