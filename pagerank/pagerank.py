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

    outgoing_links = corpus[page]
    prob_dist = dict()

    # check for page with no outgoing links
    if not outgoing_links:
        # create equal prob dist for each link
        equal_prob_dist = 1 / len(corpus)
        for link in corpus:
            prob_dist[link] = equal_prob_dist

        return prob_dist

    # Assign prob dist for pages with outgoing links
    for link in corpus:
        prob_dist[link] = (1 - damping_factor) / len(corpus)
        
        if link in outgoing_links:
            prob_dist[link] = prob_dist[link] + (damping_factor / len(outgoing_links))
        

    return prob_dist

    # raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Set up pagerank dict
    pageRank_dict = {key: 0 for key in corpus}

    pages = list(corpus.keys())
    
    # start with random page (sample n = 0)
    current_page = random.choice(pages)
    pageRank_dict[current_page] += 1

    # iterate through remaining samples
    for _ in range(n - 1):
        probs = transition_model(corpus, current_page, damping_factor)
        weights = [probs[p] for p in pages]
        next_page = random.choices(pages, weights=weights, k=1)[0]
        pageRank_dict[next_page] += 1
        current_page = next_page
        
    # convert sample visits to percentages
    for key in pageRank_dict:
        pageRank_dict[key] = pageRank_dict[key] / n

    return pageRank_dict
            
    # raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys()) 
    num_pages = len(pages)
    incoming = {p: set() for p in pages} # key: page x, value: pages that link to page x
    
    # populating incoming
    for i in pages:
        for j in corpus[i]:
            if j in pages:
                incoming[j].add(i)

    # track pages with no outlinks
    dead_ends = set()
    for page in pages:
        if not corpus[page]:
            dead_ends.add(page)

    # initialize pageRank dict
    ranks = {p: 1 / num_pages for p in pages}

    # find static teleport chance before iteration
    tp_prob = (1 - damping_factor) / num_pages

    # iterate until convergence
    while True:
        dead_end_ranks = sum(ranks[i] for i in dead_ends) # calculating PR mass for pages with no outlinks
        dead_end_prob = damping_factor * dead_end_ranks / num_pages
        
        # set up new pagerank dict for each round of page ranking
        new_ranks = dict()

        # calculate pagerank for page 
        for page in pages:
            incoming_prob = damping_factor * sum(ranks[i] / len(corpus[i]) for i in incoming[page])
            new_rank = tp_prob + dead_end_prob + incoming_prob
            new_ranks[page] = new_rank
        
        max_abs_diff = max(abs(new_ranks[key] - ranks[key]) for key in ranks)
        if max_abs_diff <= 0.001:
            ranks = new_ranks
            break
        
        ranks = new_ranks

    return ranks
             

if __name__ == "__main__":
    main()
