// Using the data in backlinks, backlinks_count, backlinks_cumsum, and
// outlinks_count, we compute the pagerank for each page id.
package main

import (
	"fmt"
	"log"
	"encoding/binary"
	"os"
	"sync/atomic"
	"sync"
	"math"
	"runtime"
)

const (
	// The damping factor used in each iteration of pagerank
	DAMPING = 0.85
	// The threshold for finishing iteration
	CHANGE_THRESHOLD = 0.0000001
)


func read_array(filename string) ([]uint32, error) {
	// The first number in the file should be the length of the subsequent
	// array
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var length uint32
	if err = binary.Read(f, binary.LittleEndian, &length); err != nil {
		return nil, err
	}

	arr := make([]uint32, length)
	err = binary.Read(f, binary.LittleEndian, arr)
	return arr, err
}

// Updates the pagerank for every page in `pagerank`. The `pagerank` array
// actually contains floating point numbers, but in order to use atomic compare
// and swap operations, the floats are encoded as uint32 values. This function
// is thread safe.
func pagerank_iter(pageranks, backlinks, backlinks_count,
	backlinks_cumsum, outlinks_count []uint32, num_pages uint32, damping float32) {
	damping_sum := (1 - damping) / float32(num_pages)

	for id := range(pageranks) {
		for {
			old := pageranks[id]
			// We use the update specified by
			// https://en.wikipedia.org/wiki/Pagerank#Simplified_algorithm
			// with the damping factor
			var start int
			if id == 0 {
				start = 0
			} else {
				start = int(backlinks_cumsum[id-1])
			}
			end := start + int(backlinks_count[id])
			sum_of_backlink_ranks := float32(0)
			for i := start; i < end; i++ {
				link := int(backlinks[i])
				term := math.Float32frombits(pageranks[link]) /
					float32(outlinks_count[link])
				sum_of_backlink_ranks += term
			}

			final := math.Float32bits(damping_sum + damping*sum_of_backlink_ranks)
			if atomic.CompareAndSwapUint32(&pageranks[id], old, final) {
				break
			}
		}
	}
}

// Returns the average difference per value
func compute_difference(pageranks, old_pageranks []uint32) (diff float32) {
	for i := range pageranks {
		diff += float32(math.Abs(float64(pageranks[i] - old_pageranks[i])))
	}
	return diff / float32(len(pageranks))
}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	backlinks, err := read_array("backlinks")
	if err != nil {
		log.Fatal(err)
	}
	backlinks_count, err := read_array("backlinks_count")
	if err != nil {
		log.Fatal(err)
	}
	backlinks_cumsum, err := read_array("backlinks_cumsum")
	if err != nil {
		log.Fatal(err)
	}
	outlinks_count, err := read_array("outlinks_count")
	if err != nil {
		log.Fatal(err)
	}

	var num_pages uint32
	for _, v := range outlinks_count {
		if v > 0 {
			num_pages++
		}
	}


	old_pageranks := make([]uint32, len(backlinks_count))
	pageranks := make([]uint32, len(backlinks_count))
	// Initialize each page rank to 1
	for i := range pageranks {
		old_pageranks[i] = math.Float32bits(1.0 / float32(len(backlinks_count)))
	}
	copy(pageranks, old_pageranks)

	// We iteratively run page rank until the difference between iterations
	// drops below some threshold
	for {
		var wg sync.WaitGroup
		for i := 0; i < 10; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				pagerank_iter(pageranks, backlinks, backlinks_count, backlinks_cumsum,
					outlinks_count, num_pages, DAMPING)
			}()
		}
		wg.Wait()

		diff := compute_difference(pageranks, old_pageranks)
		if diff < CHANGE_THRESHOLD {
			break
		}

		copy(old_pageranks, pageranks)
	}

	for i := 0; i < 10; i++ {
		fmt.Println(i, math.Float32frombits(pageranks[i]))
	}

	sum := float32(0)
	for _, rank := range pageranks {
		sum += math.Float32frombits(rank)
	}
	fmt.Println(sum)
}
