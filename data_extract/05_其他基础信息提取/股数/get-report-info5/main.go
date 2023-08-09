package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

type RawRecord struct {
	TType  string          `json:"type"`
	Inside json.RawMessage `json:"inside"`
}

type Record struct {
	TType      string
	Inside     string
	InsideList []string
}

type Tuple struct {
	Key   string
	Value string
}

// 官方txt文件输入位置,末尾需要有\\
var dir1 string = "..\\..\\..\\存放txt\\"

// 输出文件
var outfile string = "..\\..\\..\\..\\llm_demo\\data\\sharesnum.csv"

func main() {
	listfile := "./output.txt"

	ofile, _ := os.Open(listfile) // 请替换为你的文件名
	scanner := bufio.NewScanner(ofile)
	scanner.Split(bufio.ScanLines)
	var txtlines []string

	for scanner.Scan() {
		txtlines = append(txtlines, scanner.Text())
	}

	ofile.Close()

	resultFile, _ := os.Create(outfile)
	defer resultFile.Close()
	writer := bufio.NewWriter(resultFile)

	for _, eachline := range txtlines {
		// s := strings.Split(eachline, "__")[1]
		// if !strings.Contains(s, "证券") {
		// 	continue
		// }
		println(eachline)
		filePath := dir1 + eachline + ".txt"
		file, err := os.Open(filePath)
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()

		recordList := []Record{}

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			var rawRecord RawRecord
			var record Record
			err := json.Unmarshal([]byte(scanner.Text()), &rawRecord)
			if err != nil {
				log.Fatal(err)
			}
			if rawRecord.TType == "页眉" || rawRecord.TType == "页脚" {
				continue
			}
			record.TType = rawRecord.TType
			// 检查 Inside 字段是字符串还是列表
			// fmt.Println(string(rawRecord.Inside))
			s := string(rawRecord.Inside)
			if len(s) == 0 {
				continue
			}
			if s[1] == '[' {
				// 是列表
				insideList := []string{}
				a := s
				a, _ = strings.CutPrefix(a, "\"")
				a, _ = strings.CutSuffix(a, "\"")
				a = strings.ReplaceAll(a, "'", "\"")
				err = json.Unmarshal([]byte(a), &insideList)
				if err != nil {
					var insideString string
					err = json.Unmarshal(rawRecord.Inside, &insideString)
					if err != nil {
						log.Fatal(err)
					}
					record.Inside = insideString
				}
				record.InsideList = insideList
			} else {
				// 是字符串
				var insideString string
				err = json.Unmarshal(rawRecord.Inside, &insideString)
				if err != nil {
					log.Fatal(err)
				}
				record.Inside = insideString
			}
			recordList = append(recordList, record)
		}

		// tupleList := []Tuple{}
		total_shares := "0"
		for _, r := range recordList {
			if r.TType == "excel" && len(r.InsideList) >= 2 {
				the_str := r.InsideList[0]
				if strings.Contains(the_str, "股份总数") && total_shares == "0" && !strings.Contains(the_str, "流通") {
					for k := len(r.InsideList) - 1; k >= 1; k-- {
						v := r.InsideList[k]
						v = strings.ReplaceAll(v, " ", "")
						v = strings.ReplaceAll(v, ",", "")
						v = strings.ReplaceAll(v, "，", "")
						f, err2 := strconv.ParseFloat(v, 64)
						if err2 != nil {
							continue
						} else {
							if f > 100 {
								total_shares = fmt.Sprintf("%.0f", f)
								break
							}
						}
					}

				}
				the_str2 := r.InsideList[1]
				if strings.Contains(the_str2, "股份总数") && total_shares == "0" && !strings.Contains(the_str, "流通") {
					for k := len(r.InsideList) - 1; k >= 1; k-- {
						v := r.InsideList[k]
						v = strings.ReplaceAll(v, " ", "")
						v = strings.ReplaceAll(v, ",", "")
						v = strings.ReplaceAll(v, "，", "")
						f, err2 := strconv.ParseFloat(v, 64)
						if err2 != nil {
							continue
						} else {
							if f > 100 {
								total_shares = fmt.Sprintf("%.0f", f)
								break
							}
						}
					}
				}

			}
		}
		year := strings.Split(eachline, "__")[4]
		src := strings.Split(eachline, "__")[5]
		code := strings.Split(eachline, "__")[2]
		bondname := strings.Split(eachline, "__")[3]
		// resultStr := strings.Join(result, "\001")
		line := fmt.Sprintf("%s\001%s\001%s\001%s\001%s", year, src, code, bondname, total_shares)
		fmt.Fprintln(writer, line)
		writer.Flush()

	}

}
