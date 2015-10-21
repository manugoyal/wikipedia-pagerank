import numpy as np
from collections import defaultdict

def get_backlinks():
    """Returns a mapping from page ID to the list of pages that link to it"""
    backlinks = np.fromfile(open('backlinks.out'), dtype=np.uint32)[1:]
    backlinks_count = np.fromfile(open('backlinks_count.out'),
                                  dtype=np.uint32)[1:]
    backlinks_cumsum = np.fromfile(open('backlinks_cumsum.out'),
                                   dtype=np.uint32)[1:]

    output = {}
    for i in range(len(backlinks_count)):
        start = 0 if i == 0 else backlinks_cumsum[i-1]
        end = start + backlinks_count[i]
        output[i] = backlinks[start:end]

    return output

def get_outlinks(backlinks):
    """Given a mapping of backlinks, returns a mapping from page ID to the list
    of pages that it links to"""
    output = defaultdict(list)
    for id, backlinks in backlinks.iteritems():
        for backlink_id in backlinks:
            output[backlink_id].append(id)
    return output

def get_pageranks():
    """Returns a mapping from page ID to the pagerank (from the pageranks.out
    file)"""
    pageranks = np.fromfile(open('pageranks.out'), dtype=np.float32)[1:]
    return {id:pagerank for id, pagerank in enumerate(pageranks)}

def normalized_pageranks(pageranks):
    """Given a mapping from id to pagerank, returns the pageranks normalized by
    the lowest pagerank (this makes the numbers nicer) """
    minrank = min(pageranks.itervalues())
    return {id:pagerank/minrank for id, pagerank in pageranks.iteritems()}
