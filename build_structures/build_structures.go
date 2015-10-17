// From the database, builds the following arrays that we use for computing page
// rank
//
// 1. Array of backlinks to a page, ordered by the page being linked to. For
// example: If 0 links to 1 and 2, 1 links to 3, and 2 links to 1, then the
// array would look like [0, 2, 0, 1], because [0, 2] link to 1, [0] links to 2,
// and [1] links to 3.
//
// 2. Array of number of backlinks for each page. Using the previous example,
// the array would be [0, 2, 1, 1]
//
// 3. Cumulative sum of number of backlinks for each page. Using the previous
// example, the array would be [0, 2, 3, 4]
//
// 4. Number of outbound links for each page
//
// Thus, in order to get a list of backlinks for page n, I'd look at the
// cumulative sum at index n-1 (array 3, or 0 if n == 0), to get the starting
// index into the list of links (array 1), and read the number of links
// specified in array 2 at index n.
//
// These arrays are written out to files: backlinks.out, backlinks_count.out,
// backlinks_cumsum.out, outlinks_count.out, as a sequence of bytes, where the
// first item is the length of the array.

package main

import (
	"fmt"
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
	"log"
	"../util"
)

func get_array_of_ints(db *sql.DB, query string,
	args ...interface{}) ([]uint32, error) {
	rows, err := db.Query(query, args...)
	if err != nil {
		return nil, err
	}

	defer rows.Close()
	var result []uint32
	for rows.Next() {
		var num uint32
		err = rows.Scan(&num)
		if err != nil {
			return nil, err
		}
		result = append(result, num)
	}
	return result, rows.Err()
}

func get_int(db *sql.DB, query string, args ...interface{}) (uint32, error) {
	var result uint32
	err := db.QueryRow(query, args...).Scan(&result)
	return result, err
}

func populate_outlinks_count(db *sql.DB, outlinks_count []uint32) error {
	rows, err := db.Query("SELECT `pl_from_id`, COUNT(*) FROM " +
		"`pl_essential` GROUP BY `pl_from_id`")
	if err != nil {
		return err
	}

	defer rows.Close()

	// Initialize all counts to 0
	for i := range outlinks_count {
		outlinks_count[i] = 0
	}

	for rows.Next() {
		var id, count uint32
		err = rows.Scan(&id, &count)
		if err != nil {
			return err
		}
		outlinks_count[id] = count
	}

	return rows.Err()
}

func main() {
	db, err := sql.Open("mysql", "root@/simple_english_wikipedia")
	if err != nil {
		log.Fatal(err);
	}

	pageIds, err := get_array_of_ints(
		db, "SELECT `page_id` FROM `page_essential`")
	if err != nil {
		log.Fatal(err);
	}

	var maxId uint32 = 0
	for _, id := range pageIds {
		if maxId < id {
			maxId = id
		}
	}

	total_links, err := get_int(db, "SELECT COUNT(*) FROM `pl_essential`")
	if err != nil {
		log.Fatal(err)
	}

	backlinks := make([]uint32, total_links)
	backlinks_count := make([]uint32, maxId + 1)
	backlinks_cumsum := make([]uint32, maxId + 1)
	prevcumsum := 0
	for id := uint32(0); id <= maxId; id++ {
		if id % 1000 == 0 {
			fmt.Println(id)
		}
		id_backlinks, err := get_array_of_ints(
			db, "SELECT `pl_from_id` from `pl_essential` " +
				"WHERE `pl_to_id` = ?", id)
		if err != nil {
			log.Fatal(err);
		}
		backlinks_count[id] = uint32(len(id_backlinks))
		backlinks_cumsum[id] = uint32(len(id_backlinks) + prevcumsum)
		copy(backlinks[prevcumsum:prevcumsum+len(id_backlinks)],
			id_backlinks)
		prevcumsum += len(id_backlinks)
	}

	outlinks_count := make([]uint32, maxId + 1)
	if err = populate_outlinks_count(db, outlinks_count); err != nil {
		log.Fatal(err)
	}

	fmt.Println("Writing backlinks")
	util.WriteArray("backlinks.out", backlinks)
	fmt.Println("Writing backlinks count")
	util.WriteArray("backlinks_count.out", backlinks_count)
	fmt.Println("Writing backlinks cumsum")
	util.WriteArray("backlinks_cumsum.out", backlinks_cumsum)
	fmt.Println("Writing outlinks_count")
	util.WriteArray("outlinks_count.out", outlinks_count)
}
