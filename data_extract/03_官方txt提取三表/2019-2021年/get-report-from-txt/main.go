package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
)

// 官方txt文件输入位置,末尾需要有\\
var dir_in string = "..\\..\\..\\存放txt\\"

// 提取的三表输出位置,末尾需要有\\
var dir_out string = "..\\..\\..\\数据处理过程目录\\txt抽取三表19到21\\"

type Tuple struct {
	key   string
	value string
}

type Report struct {
	balance  []Tuple
	profit   []Tuple
	cashflow []Tuple
}

type RawRecord struct {
	TType  string          `json:"type"`
	Inside json.RawMessage `json:"inside"`
}

type Record struct {
	TType      string
	Inside     string
	InsideList []string
}

func extract(recordList []Record) Report {
	conditionFlag := 0
	var report Report
	balance := []Tuple{}
	profit := []Tuple{}
	cashflow := []Tuple{}

	//状态1，进入财务报表
	//状态2：找到合并资产负债表
	//状态3：退出合并资产负债表，找寻合并利润表
	//状态4：找到合并利润表 -> 2 3状态都可以直接转移到4
	//状态5：退出合并利润表，找寻合并现金流量表
	//状态6：找到合并现金流量表 -> 4 5 状态都可以直接转移到6
	for i := 0; i < len(recordList); i++ {
		record := recordList[i]
		if conditionFlag == 0 && record.TType == "text" && strings.HasSuffix(record.Inside, "财务报表") && strings.HasPrefix(record.Inside, "二") {
			conditionFlag = 1
		} else if conditionFlag == 1 && record.TType == "text" && strings.HasSuffix(record.Inside, "合并资产负债表") {
			conditionFlag = 2
		} else if conditionFlag == 2 && record.TType == "excel" {
			s := record.InsideList
			if len(s) == 3 {
				balance = append(balance, Tuple{s[0], s[1]})
			} else if len(s) == 4 {
				balance = append(balance, Tuple{s[0], s[2]})
			}
		} else if conditionFlag == 2 && record.TType == "text" && strings.HasSuffix(record.Inside, "母公司资产负债表") {
			conditionFlag = 3
		} else if (conditionFlag == 2 || conditionFlag == 3) && record.TType == "text" && strings.HasSuffix(record.Inside, "合并利润表") {
			conditionFlag = 4
		} else if conditionFlag == 4 && record.TType == "excel" {
			s := record.InsideList
			if len(s) == 3 {
				profit = append(profit, Tuple{s[0], s[1]})
			} else if len(s) == 4 {
				profit = append(profit, Tuple{s[0], s[2]})
			}
		} else if conditionFlag == 4 && record.TType == "text" && strings.HasSuffix(record.Inside, "母公司利润表") {
			conditionFlag = 5
		} else if (conditionFlag == 4 || conditionFlag == 5) && record.TType == "text" && strings.HasSuffix(record.Inside, "合并现金流量表") {
			conditionFlag = 6
		} else if conditionFlag == 6 && record.TType == "excel" {
			s := record.InsideList
			if len(s) == 3 {
				cashflow = append(cashflow, Tuple{s[0], s[1]})
			} else if len(s) == 4 {
				cashflow = append(cashflow, Tuple{s[0], s[2]})
			}
		} else if conditionFlag == 6 && record.TType == "text" && (strings.HasSuffix(record.Inside, "母公司现金流量表") || strings.HasSuffix(record.Inside, "合并所有者权益变动表")) {
			break
		}
	}
	report.balance = balance
	report.cashflow = cashflow
	report.profit = profit
	return report
}

func get_all_report(filepath string) {
	filePreName := strings.Split(filepath, "\\")[len(strings.Split(filepath, "\\"))-1]
	balanceFileName := dir_out + filePreName + "_balance.txt"
	profitFileName := dir_out + filePreName + "_profit.txt"
	cashflowFileName := dir_out + filePreName + "_cashflow.txt"

	file, err := os.Open(filepath)
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
	report := extract(recordList)

	balanceFile, _ := os.Create(balanceFileName)
	defer balanceFile.Close()

	balanceWriter := bufio.NewWriter(balanceFile)

	for _, t := range report.balance {
		fmt.Fprintln(balanceWriter, strings.ReplaceAll(t.key, "\n", "")+"\001"+strings.ReplaceAll(t.value, "\n", ""))
	}

	balanceWriter.Flush()

	profitFile, _ := os.Create(profitFileName)
	defer profitFile.Close()

	profitWriter := bufio.NewWriter(profitFile)

	for _, t := range report.profit {
		fmt.Fprintln(profitWriter, strings.ReplaceAll(t.key, "\n", "")+"\001"+strings.ReplaceAll(t.value, "\n", ""))
	}

	profitWriter.Flush()

	cashflowFile, _ := os.Create(cashflowFileName)
	defer cashflowFile.Close()

	cashflowWriter := bufio.NewWriter(cashflowFile)

	for _, t := range report.cashflow {
		fmt.Fprintln(cashflowWriter, strings.ReplaceAll(t.key, "\n", "")+"\001"+strings.ReplaceAll(t.value, "\n", ""))
	}

	cashflowWriter.Flush()

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

}

func get_all_report_txt() {
	// 要遍历的文件夹路径
	dir := dir_in

	file, err := os.Open("./output.txt")
	if err != nil {
		log.Fatalf("failed to open file: %s", err)
	}

	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var txtlines []string

	for scanner.Scan() {
		txtlines = append(txtlines, scanner.Text())
	}

	file.Close()

	for _, eachline := range txtlines {
		fmt.Println(dir + eachline + ".txt")
		get_all_report(dir + eachline + ".txt")
	}
}

func main() {
	get_all_report_txt()
}
