
# coding: utf-8

# In[132]:

import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')

import numpy as np
from collections import defaultdict

def get_backlinks():
    """Returns a mapping from page ID to the list of pages that link to it"""
    dt = np.dtype('uint32').newbyteorder('<') # It's little endian data
    backlinks = np.fromfile('backlinks.out', dtype=dt)[1:]
    backlinks_count = np.fromfile('backlinks_count.out', dtype=dt)[1:]
    backlinks_cumsum = np.fromfile('backlinks_cumsum.out', dtype=dt)[1:]

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
    pageranks = np.fromfile('pageranks.out',
                            dtype=np.dtype('float32').newbyteorder('<'))[1:]
    return {id:pagerank for id, pagerank in enumerate(pageranks)}

def normalized_pageranks(pageranks):
    """Given a mapping from id to pagerank, returns the pageranks normalized by
    the lowest pagerank (this makes the numbers nicer) """
    minrank = min(pageranks.itervalues())
    return {id:pagerank/minrank for id, pagerank in pageranks.iteritems()}

def get_restricted_pages():
    """Returns a set of pages that we can't edit due to access restrictions"""
    return set(np.fromfile('restricted_pages.out', dtype=np.dtype('<u4'))[1:])


# In[133]:

#page if:backlinks dictionary
mapping_dic=get_backlinks()


# In[135]:

#getting pageranks
pageranks=get_pageranks()
#getting normalized ranks as a list
norm_ranks=normalized_pageranks(pageranks)


# In[136]:

#getting only rank values from normalized ranks dictionary
norm_ranks=norm_ranks.values()
#lets see min, max, mean, and percentiles of all normalized rank values
print(np.percentile(norm_ranks, [10, 50, 60,70,80,90,91,92,93,94,95,96,97,98,99,99.9]))
print(np.percentile(norm_ranks, 99))
print(np.mean(norm_ranks))
print(np.min(norm_ranks))
print(np.max(norm_ranks))


# In[137]:

#average normalized rank value
sum(norm_ranks)/len(norm_ranks)


# In[138]:

#k=10069 #B
#k=100  #A

#lets see histograms of rank values of some random IDs
k=100
ranklist_100=[norm_ranks[key] for key in mapping_dic[k]]
print(len(ranklist_100))
if len(ranklist_100)>1 :
    np.histogram(ranklist_100)
    plt.hist(ranklist_100, bins=50)



# In[139]:

#lets see histograms of rank values of some random IDs
k=10069
ranklist_100=[norm_ranks[key] for key in mapping_dic[k]]
print(len(ranklist_100))
if len(ranklist_100)>1 :
    np.histogram(ranklist_100)
    plt.hist(ranklist_100, bins=50)


# In[140]:

# Testing if a page is a spam. In this test, page is a spam if at least num_page=0.8 percentage
# of its backlinks are greater than rank_thresh=96 percentile of all ranks (norm_ranks), then it is a spam
# page. The reasoning behind is that on the spectrum of all rank values, if rank values of the majority
# of its backlinks are skewed to the extreme-right end, the it is likely that it is a spam.

rank_thresh=96
num_page=0.8

def strict_test(id):
    ranklist=[norm_ranks[page] for page in mapping_dic[id]]
    if len(ranklist)==0:
        return False
    num=sum(k>np.percentile(norm_ranks, rank_thresh) for k in ranklist)
    if num>(num_page)*len(ranklist):
        return True
    else:
        return False


# In[141]:

# In this test, a page is a spam if ranks of at least 75% of all backlinks are
# in 4rd/highest quarter of its ranklist, and those ranks are all greater than
# the major_tresh=75 percentile of all ranks (norm_ranks). The reasoning behind
# this is that a page is spam if its distribution is skewed to the right and
# ranks of those skewed backlinks are also very high.

major_tresh=75

def loose_test(id):
    ranklist=[norm_ranks[page] for page in mapping_dic[id]]
    if len(ranklist)==0:
        return False
    ranklist_length=len(ranklist)
    high_list=[i for i in ranklist if i>=np.percentile(norm_ranks, major_tresh)]
    if len(high_list)>=0.75*len(ranklist) and min(high_list)>=np.percentile(ranklist, 0.75):
        return True
    else:
        return False

# In[142]:

#random_ids=[100, 4626, 234567, 5342, 237, 3468, 654, 23456, 543, 467123, 123453]
#s_list=[strict_test(id) for id in random_ids]
#l_list=[loose_test(id) for id in random_ids]

