// Utility functions
package util

import (
	"os"
	"encoding/binary"
)

func WriteArray(filename string, arr []uint32) error {
	// We first write the length, then the data as a binary stream, in
	// LittleEndian order
	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	if err = binary.Write(f, binary.LittleEndian, uint32(len(arr)));
	err != nil {
		return err
	}

	for _, v := range arr {
		if err = binary.Write(f, binary.LittleEndian, v); err != nil {
			return err
		}
	}
	return nil
}

func ReadArray(filename string) ([]uint32, error) {
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
