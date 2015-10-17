import numpy as np

values = np.fromfile(open('pageranks.out'), dtype=np.float32)
pageranks = values[1:] # Since the first item is the length

normalized_pageranks = pageranks / np.min(pageranks)
biggest_rank = np.argmax(normalized_pageranks)
print 'Page %d has the highest normalized pagerank of %f' % (
    biggest_rank, normalized_pageranks[biggest_rank])
