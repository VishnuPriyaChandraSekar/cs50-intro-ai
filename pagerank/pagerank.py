import copy
import os
import random
import re
import sys

import numpy as np

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_probability = dict()
    total_pages_in_corpus = len(corpus)
    prob_reach_page_from_rand = (1 - damping_factor)/total_pages_in_corpus
    outgoing_links = corpus.get(page)
    total_outgoing_links = len(outgoing_links)
    ## if there are no outgoing links then each page in the corpus gets equal probability from random page
    if total_outgoing_links == 0:
        for document in corpus:
            transition_probability[document] = 1/total_pages_in_corpus
        return transition_probability

    for document in corpus:
        # all documents will be reached by random clicks
        transition_probability[document] = prob_reach_page_from_rand
        # probability to each the linked document is equal to (sum of the page rank)/total outgoing link.
        if document in outgoing_links:
            transition_probability[document] += (damping_factor/total_outgoing_links)
    return transition_probability

def get_total_incoming_links(corpus, page):
    total_incoming_link = 0
    for document in corpus:
        if page in corpus[document]:
            total_incoming_link += 1
    return total_incoming_link

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict()
    for page in corpus:
        page_rank[page] = 0

    page = random.choice(list(corpus.keys()))
    page_rank[page] += 1
    for i in range(n-1):
        next_pages = transition_model(corpus, page, damping_factor)
        page = random.choices(list(next_pages.keys()), weights=list(next_pages.values()), k=1)[0]
        page_rank[page] += 1

    for page in page_rank:
        page_rank[page] = page_rank[page]/n
    return page_rank



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    documents_list = list(corpus.keys())
    prob_from_rand_page = (1 - damping_factor)/n
    rank_vector = np.full((1, n), 1/n)
    link_matrix = initialize_link_matrix(corpus, n)
    is_not_convergent = True
    finalized_page_rank = dict()
    while is_not_convergent:
        previous_rank_vector = copy.deepcopy(rank_vector)
        rank_vector = (rank_vector @ link_matrix) * damping_factor + prob_from_rand_page
        diff_vector = rank_vector - previous_rank_vector
        is_not_convergent = not np.all(np.abs(diff_vector) <= 0.001)

    for i in range(n):
        finalized_page_rank[documents_list[i]] = rank_vector[0][i]
    return finalized_page_rank

def initialize_link_matrix(corpus, n):
    link_matrix = np.zeros((n, n))
    documents_list = list(corpus.keys())
    for document in corpus:
        parent_pages = list(corpus[document])
        i = documents_list.index(document)
        if len(parent_pages) > 0:
            for page in parent_pages:
                j = documents_list.index(page)
                link_matrix[i][j] = 1/len(parent_pages)
        else:
            for j in range(n):
                link_matrix[i][j] = 1/n
    return link_matrix



if __name__ == "__main__":
    main()
