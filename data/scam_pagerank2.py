# Tool that suggests ways to artificially inflate your pagerank, without the
# restriction that you can only edit public pages.

import data_utils
import pagerank_utils
import copy
import numpy as np

def get_clean_data():
    """Returns the true pageranks, backlinks, outlinks_count, etc for wikipedia
    as a map. This dict should be passed around unmodified to the tool"""
    pageranks = data_utils.get_pageranks()
    backlinks = data_utils.get_backlinks()
    editable_pages = backlinks.keys() # This is all the pages

    return {
        # Mapping from id to raw pagerank
        'pageranks': pageranks,
        # Mapping from id to normalized pagerank
        'normalized_pageranks': data_utils.normalized_pageranks(pageranks),
        # Mapping from id to list of backlinks
        'backlinks': backlinks,
        # Mapping from id to number of outlinks
        'outlinks_count': data_utils.get_outlinks_count(),
        # List of pages we can edit
        'editable_pages': editable_pages
    }


def get_current_page_rank(data, page_id):
    return data['normalized_pageranks'][page_id]

def inflate_page_rank(data, page_id, amount):
    """Try to increase the normalized page rank roughly to the given amount.
    Returns the amount we predict the increase to be, and the list of pages to
    edit to make it happen."""
    inflation_factor = float(amount) / data['normalized_pageranks'][page_id]
    raw_target_pagerank = data['pageranks'][page_id] * inflation_factor

    # By adding a link from a page with rank r and number of outbound links k,
    # we'll get roughly a page rank boost of d*(r/(k+1)), where d is the damping
    # factor.
    pagerank_boost = lambda id: (pagerank_utils.DAMPING *
                                 data['pageranks'][id] /
                                 (data['outlinks_count'][id] + 1))
    raw_pagerank_delta = raw_target_pagerank - data['pageranks'][page_id]

    # Sort the entire set of pages by approximately how much page rank they
    # could lend to us
    editable_pages = sorted(data['editable_pages'],
                            key=pagerank_boost, reverse=True)

    # Go down the list of editable pages, and keep adding pages to the list
    # until we hit our target. Note that we can't add pages that already have a
    # link to our page, because in general, wikipedia doesn't duplicate links
    # between pages
    total_boost = 0
    pages_to_edit = []
    for id in editable_pages:
        if total_boost > raw_pagerank_delta:
            break
        if id in data['backlinks'][page_id]:
            continue
        total_boost += pagerank_boost(id)
        pages_to_edit.append(id)

    normalized_boost = (total_boost / data['pageranks'][page_id] *
                        data['normalized_pageranks'][page_id])
    return normalized_boost, pages_to_edit

def evaluate_scam(data, page_id, pages_to_edit):
    """Given a clean data set, a page to inflate the rank of, and a list of
    pages to add links to the target page, return the new normalized pagerank of
    the page"""

    new_backlinks = copy.copy(data['backlinks'])
    new_outlinks_count = copy.copy(data['outlinks_count'])
    # Link the pages_to_edit to the page_id
    for id in pages_to_edit:
        new_backlinks[page_id] = np.append(new_backlinks[page_id], id)
        new_outlinks_count[id] += 1

    # Run pagerank on the new dataset
    new_pageranks = pagerank_utils.converge_pageranks(
        data['pageranks'], new_backlinks, new_outlinks_count)

    # Return the new normalized pagerank
    return new_pageranks[page_id] / min(new_pageranks.itervalues())
