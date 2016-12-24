import re
import os
import requests
import json
import codecs
from collections import defaultdict
from time import sleep

words = []
word_list = defaultdict(list)

app_id = 'dc09c612'
app_key = '4db4f918c6095d04d49ce8efbac67ca0'
language = 'en'

with open("barron-raw.txt", 'r') as fd:
    word = None
    for line in fd:
        line = re.sub(r'\\n', '', line)
        if line.find(".") == -1:
            word = line
            words.append(word)
        else:           
            word_list[word].append(line)            

i = 0
sorted_words = list(sorted(words))

while len(sorted_words) > 0:
    if i % 50 == 0:
        print "Created a new list: {}".format(i / 50 + 1)
    fo = codecs.open("List " + str(i / 50 + 1) + ".md", "a", "utf-8")

    w = sorted_words[0]
    fo.write("## ")
    fo.write(w.decode('utf-8'))

    # find english translation
    fo.write("\n#### English:\n")
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + w.lower()

    try:
        r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
        sorted_words.pop(0)

        if r.status_code == 200:
            data = r.json()
            for lexical_entry in data["results"][0]["lexicalEntries"]:
                for entry in lexical_entry["entries"]:          
                    for sense in entry["senses"]:
                        try:
                            definition = sense["definitions"][0] + "\n"
                            fo.write("  - " + re.sub(r':', '.', definition))
                        except KeyError as err:
                            print "Parse definition err: {}".format(err)
        else:
            print "Error parsing: {}".format(w)

        fo.write("\n#### Chinese:\n")
        for v in word_list[w]:
            fo.write("  - ")
            fo.write(v.decode('utf-8'))     
        fo.write("\n")

        i += 1
        if i % 50 == 0:
            print "{} words have been translated.".format(i)

    except requests.exceptions.ConnectionError:
        print "Connection refused by maximum connection. Sleep for 10s..."
        sleep(10)

    fo.close()
