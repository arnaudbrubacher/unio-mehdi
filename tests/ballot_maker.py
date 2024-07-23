import json
import pprint
# Opening JSON file
import os 
import datetime
import matplotlib.pyplot as plt

def create_ballot(sample_path, ballot_id, vote_1, vote_2):
    f = open(sample_path)
    


    sample = json.load(f)
    f.close()
    pprint.pprint(sample)

    if vote_1 == "f":
        vote_label_1 = "for"
    elif vote_1 == "a":
        vote_label_1 = "against"
    elif vote_1 == "b":
        vote_label_1 = "abstain"

    if vote_2 == "f":
        vote_label_2 = "for"
    elif vote_2 == "a":
        vote_label_2 = "against"
    elif vote_2 == "b":
        vote_label_2 = "abstain"

    sample['object_id'] = f"ballot-{ballot_id}"

    sample['contests'][0]["ballot_selections"][0]["object_id"] = f"Q1-{vote_label_1}-selection"
    sample['contests'][1]["ballot_selections"][0]["object_id"] = f"Q2-{vote_label_2}-selection"

    pprint.pprint(sample)
    output = open(os.path.join(SAVE_PATH, f"ballot-{ballot_id}.json"), "w")
    # magic happens here to make it pretty-printed
    output.write(json.dumps(sample, indent=4, sort_keys=True))
    output.close()

# def chart(occurance_list):
#     hour_list = [t.hour for t in occurance_list]
#     print hour_list
#     numbers=[x for x in xrange(0,24)]
#     labels=map(lambda x: str(x), numbers)
#     plt.xticks(numbers, labels)
#     plt.xlim(0,24)
#     plt.hist(hour_list)
#     plt.show()

SAMPLE_PATH = '/home/zero/o/unio/data/FSSS/sample_ballot.json'
PLAINS_PATH = '/home/zero/o/unio/data/FSSS/plains.txt'
SAVE_PATH = "/home/zero/o/unio/data/FSSS/ballots"

plains = open(PLAINS_PATH)

id_list = []
q1_list = []
q2_list = []
time_list = []
for line in plains:
    tokens = line.split("\t")
    i = 0
    for t in tokens:
        if i != 0:
            if i == 1:
                id_list.append(t.strip())
            elif i == 2:
                q1_list.append(t.strip())
            elif i == 3:
                q2_list.append(t.strip())
            elif i == 4:
                parts = t.strip().upper().split(" ")
                new_time = parts[-2].replace(".", "") + " " + parts[-1].replace(".", "")
                print(new_time)
                try:
                    dt = datetime.datetime.strptime(new_time, "%I:%M %p")
                except Exception as ex:
                    dt = datetime.datetime.strptime(new_time, "%I %p")

                time_list.append(dt.hour)

        i += 1

# print(time_list)

numbers=[x for x in range(0,24)]
labels=map(lambda x: str(x), numbers)
plt.text(0,75,"FSSS Voting, 21 Sep. 2023 Hourly Histogram - Until 16h00")
plt.xticks(numbers, labels)
plt.xlim(0,24)
plt.hist(time_list)
plt.show()

# print(q1_list)
# print(q2_list)
# print(len(id_list), len(q1_list), len(q2_list))

# for i in range(len(id_list)):
#     create_ballot(SAMPLE_PATH, id_list[i], q1_list[i], q2_list[i])

# print(os.listdir(SAVE_PATH))
# print(len(os.listdir(SAVE_PATH)))
