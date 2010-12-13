import cfnamegen
GREAT_DEMON_LENGTH = (11, 13)
MIDDLE_DEMON_LENGTH = (5, 7)
SMALL_DEMON_LENGTH = (4, 7)

GreatDemonGrammar = {
        "name": ["<nameStart><nameMiddle0to2><nameEnd>"],
        "nameMiddle0to2": ["","<nameMiddle>", "<nameMiddle><nameMiddle>"],
        "nameStart": ["<nsCons><nmVowel>", "<nsCons><nmVowel>", "<nsCons><nmVowel>", "<nsVowel>"],
        "nameMiddle": ["<nmCons><nmVowel>"],
        "nameEnd": ["<neCons><neVowel>", "<neCons>", "<neCons>"],
        "nsCons": ["J", "M", "P", "N", "Y", "D", "F"],
        "nmCons": ["l", "m", "lm", "th", "r", "s", "ss", "p", "f", "mb", "b", "lb", "d", "lf"],
        "neCons": ["r", "n", "m", "s", "y", "l", "th", "b", "lb", "f", "lf"],
        "nsVowel": ["A", "Au", "Ei"],
        "nmVowel": ["a", "e", "i", "o", "u", "au", "oa", "ei"],
        "neVowel": ["e", "i", "a", "au"]
        }

GreatDemonGen = cfnamegen.CFNameGen(GreatDemonGrammar) 

def get_great_demon():
    while True:
        name = GreatDemonGen.getName()
        if GREAT_DEMON_LENGTH[0]<len(name)<GREAT_DEMON_LENGTH[1]:
            return name

def get_middle_demon():
    while True:
        name = GreatDemonGen.getName()
        if MIDDLE_DEMON_LENGTH[0]<len(name)<MIDDLE_DEMON_LENGTH[1]:
            return name


def get_small_demon():
    while True:
        name = GreatDemonGen.getName()
        if SMALL_DEMON_LENGTH[0]<len(name)<SMALL_DEMON_LENGTH[1]:
            if all([c.lower() in "abcdefg" for c in name]):
                return name
if __name__=="__main__":
    print "Great demon: ", get_great_demon()
    print "Middle demon: ", get_middle_demon()
    print "Small demon: ", get_small_demon()
    