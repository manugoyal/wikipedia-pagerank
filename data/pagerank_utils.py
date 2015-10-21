# This stuff is largely copied from compute_pagerank.go
import numpy as np

# The damping factor used in each iteration of pagerank
DAMPING = 0.85
# The threshold for finishing iteration
CHANGE_THRESHOLD = 0.0000001

def get_num_pages(outlinks_count):
    """Gets the actual number of page ids there are (we only count pages that
    have a nonzero number of outlinks)"""
    return sum([count > 0 for count in outlinks_count])

def get_optimized_pageranks(pageranks):
    """Returns the array version of the pageranks dict"""
    return np.array([pageranks[id] for id in range(len(pageranks))],
                    dtype=np.float32)

def get_optimized_backlinks(backlinks):
    """Turns the backlinks into backlinks, backlinks_count, and
    backlinks_cumsum"""
    backlinks_arr = np.concatenate(
        [backlinks[id] for id in range(len(backlinks))])
    backlinks_count = np.array(
        [len(backlinks[id]) for id in range(len(backlinks))])
    backlinks_cumsum = np.cumsum(backlinks_count)
    return backlinks_arr, backlinks_count, backlinks_cumsum


def get_optimized_outlinks_count(outlinks_count):
    """Turns the outlinks_count dict into an array"""
    return np.array(outlinks_count.values())

def pagerank_iter(pageranks, backlinks, backlinks_count,
                  backlinks_cumsum, outlinks_count, num_pages, damping):
    """Runs one iteration of pagerank on the existing data. Not thread safe.

    Args: (see compute_pagerank.go, except pageranks actually does contain
    floats) """
    damping_sum = (1-damping) / float(num_pages)
    with np.errstate(divide='ignore'):
        sum_terms = pageranks / outlinks_count
    update_terms = sum_terms[[backlinks]]
    start = 0
    for id in range(len(pageranks)):
        backlinks_term = np.sum(update_terms[start:start+backlinks_count[id]])
        start = backlinks_cumsum[id]
        pageranks[id] = damping_sum + damping*backlinks_term

def compute_difference(pageranks, old_pageranks):
    """Returns the average difference per id between the pagerank
    dictionaries"""
    diff = float(0)
    for i in range(len(pageranks)):
        diff += abs(pageranks[i] - old_pageranks[i])
    return diff / len(pageranks)

def converge_pageranks(pageranks, backlinks, outlinks_count):
    """Given the dictionary version of pageranks, backlinks, and outlinks_count,
    re-runs pagerank until it converges"""
    pageranks = get_optimized_pageranks(pageranks)
    backlinks, backlinks_count, backlinks_cumsum = get_optimized_backlinks(
        backlinks)
    outlinks_count = get_optimized_outlinks_count(outlinks_count)
    num_pages = get_num_pages(outlinks_count)


    new_pageranks = pageranks.copy()
    pagerank_iter(new_pageranks, backlinks, backlinks_count, backlinks_cumsum,
                  outlinks_count, num_pages, DAMPING)
    diff = compute_difference(new_pageranks, pageranks)
    while diff > CHANGE_THRESHOLD:
        print diff
        pageranks = new_pageranks
        new_pageranks = pageranks.copy()
        pagerank_iter(new_pageranks, backlinks, backlinks_count,
                      backlinks_cumsum, outlinks_count, num_pages, DAMPING)
        diff = compute_difference(new_pageranks, pageranks)
    return {id:new_pageranks[id] for id in range(len(new_pageranks))}
