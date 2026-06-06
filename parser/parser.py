import glob
import re

import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S  -> NP VP
S  -> NP VP Conj NP VP | NP VP Conj VP
VP -> V | V NP | V NP PP | V Adv | V PP | Adv V NP | V PP Adv
NP -> N | Det N | Det Adj N | Det Adj Adj N | Det Adj Adj Adj N | NP PP 
PP -> P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()
    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")
    parse_sentence(s)


def testing():
    text_files = glob.glob("sentences/*.txt")
    for file in text_files:
        with open(file) as f:
            s = f.read()
            parse_sentence(s)


def parse_sentence(s):
    # Convert input into list of words
    s = preprocess(s)
    print("Input String : ", s)
    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    print(sentence)
    words = list()
    for word in nltk.tokenize.word_tokenize(sentence):
        matched = re.search("\w+", word)
        if matched is not None:
            words.append(word.lower())
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np = list()
    subtrees = sorted(tree.subtrees(lambda t: t.label() == "NP"), key=lambda st: st.height(), reverse=True)

    for i in range(len(subtrees) - 1):
        contains_subtree = False
        for j in range(i + 1, len(subtrees)):
            contains_subtree |= subtrees[j] in subtrees[i].subtrees()
        if contains_subtree is False:
            np.append(subtrees[i])
    if subtrees[len(subtrees) - 1].label() == "NP":
        np.append(subtrees[len(subtrees) - 1])
    return np


if __name__ == "__main__":
    main()
