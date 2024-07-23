import json
import os
json_path ="/home/zero/o/unio/tests/election_record/"

json_files = ["context.json", "manifest.json","encrypted_tally.json", "tally.json", "coefficients.json", "constants.json", "guardians/guardian_UNIO-Guardian.json", "encryption_devices/device_34762797931092.json"]

for jf in json_files:
    f = open(json_path + jf)
    

    json_content = json.load(f)
    f.close()

    json_formatted_str = json.dumps(json_content, indent=2)

    with open(json_path + jf, "w") as outfile:
        outfile.write(json_formatted_str)

ballots_path = "/home/zero/o/unio/tests/election_record/submitted_ballots/"

for b in os.listdir(ballots_path):
    f = open(ballots_path + b)
    

    json_content = json.load(f)
    f.close()

    json_formatted_str = json.dumps(json_content, indent=2)

    with open(ballots_path + b, "w") as outfile:
        outfile.write(json_formatted_str)