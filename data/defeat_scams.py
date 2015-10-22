import scipy.sparse as sparse
import copy
import numpy as np

def get_probability_matrix(pageranks, backlinks, outlinks):
    # Returns a sparse probability matrix for the markov chain. We add self
    # loops to help with stuff. The inputs might get screwed
    for id in range(len(pageranks)):
        outlinks[id].append(id)
    outlinks_triples = np.array([np.array([from_id, to_id, 1.0/len(to_ids)])
                                 for from_id, to_ids in outlinks.iteritems()
                                 for to_id in to_ids])
    return sparse.csc_matrix(
        (outlinks_triples[:,2],
         (outlinks_triples[:, 0], outlinks_triples[:, 1])),
        (len(pageranks), len(pageranks)))

def mcl_iter(m):
    # Given a sparse probability matrix, runs one iteration of MCL with power 2
    print 'Computing m_squared'
    m_squared = m*m
    m_squared = m_squared.multiply(m_squared)

    print 'Computing m_div'
    m_div = m_squared.sum(1)
    m_div = np.divide(np.ones(m_div.shape), m_div)
    m_div = m_div.reshape(m_squared.shape[0], 1)
    m_div = sparse.csc_matrix(m_div)

    print 'Doing multiplication'
    return m_squared.multiply(m_div)
