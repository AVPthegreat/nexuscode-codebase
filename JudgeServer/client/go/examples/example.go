package main

import (
	"fmt"
	"os"
	"time"

	judge "github.com/QingdaoU/JudgeServer/client/go"
)

var (
	cSrc = `
#include <stdio.h>
int main(){
	int a, b;
	scanf("%d%d", &a, &b);
	printf("%d\n", a+b);
	return 0;
}
`
	cppSrc = `
#include <iostream>

using namespace std;

int main()
{
	int a,b;
	cin >> a >> b;
	cout << a+b << endl;
	return 0;
}
`
	javaSrc = `
import java.util.Scanner;
public class Main{
	public static void main(String[] args){
		Scanner in=new Scanner(System.in);
		int a=in.nextInt();
		int b=in.nextInt();
		System.out.println(a + b);
	}
}
`
	py3Src = `
s = input()
s1 = s.split(" ")
print(int(s1[0]) + int(s1[1]))
`
)

func main() {
	// How to run this example
	// - Ensure JudgeServer is running and reachable
	// - Set env:
	//     export JUDGE_ENDPOINT="http://127.0.0.1:12358"
	//     export JUDGE_TOKEN="CHANGE_THIS"            # raw token; client hashes it automatically
	//     export JUDGE_TEST_CASE_ID="normal"          # must exist under the JudgeServer's /test_case
	// - Then run (GOPATH mode works fine for this repo):
	//     GO111MODULE=off go run example.go

	endpoint := getenv("JUDGE_ENDPOINT", "http://127.0.0.1:12358")
	token := getenv("JUDGE_TOKEN", "CHANGE_THIS")
	testCaseID := getenv("JUDGE_TEST_CASE_ID", "normal")

	client := judge.NewClient(
		judge.WithEndpointURL(endpoint),
		judge.WithToken(token),
		judge.WithTimeout(10*time.Second),
	)

	// Align language configs with our current JudgeServer image
	// Java: remove legacy security manager flags
	javaCfg := *judge.JavaLangConfig
	javaCfg.RunConfig.Command = "/usr/bin/java -cp {exe_dir} -XX:MaxRAM={max_memory}k Main"

	// Python3: run source directly with -BS; avoid versioned .pyc exe name
	py3Cfg := *judge.PY3LangConfig
	py3Cfg.CompileConfig.ExeName = "solution.py"
	py3Cfg.RunConfig.Command = "/usr/bin/python3 -BS {exe_path}"

	fmt.Println("ping:")
	resp, err := client.Ping()
	if err != nil {
		// This err is an error that occurred on the client side. For example, json encoding failed
		fmt.Printf("ping client error. error is: %v.\n", err)
	} else if resp.Err() != nil {
		// This resp.Err() is the error returned by JudgeServer. For example, token error TokenVerificationFailed
		fmt.Printf("ping server error. error is: %v.\n", resp.Err().Error())
	} else {
		fmt.Println(resp.Data())
	}
	fmt.Println()

	fmt.Println("cpp_judge")
	resp, err = client.JudgeWithRequest(&judge.JudgeRequest{
		Src:            cppSrc,
		LanguageConfig: judge.CPPLangConfig,
		MaxCpuTime:     1000,
		MaxMemory:      128 * 1024 * 1024,
		TestCaseId:     testCaseID,
	})
	handleResp("cpp_judge", resp, err)
	fmt.Println()

	fmt.Println("java_judge")
	resp, err = client.JudgeWithRequest(&judge.JudgeRequest{
		Src:            javaSrc,
		LanguageConfig: &javaCfg,
		MaxCpuTime:     1000,
		MaxMemory:      256 * 1024 * 1024,
		TestCaseId:     testCaseID,
	})
	handleResp("java_judge", resp, err)
	fmt.Println()

	fmt.Println("py3_judge")
	resp, err = client.JudgeWithRequest(&judge.JudgeRequest{
		Src:            py3Src,
		LanguageConfig: &py3Cfg,
		MaxCpuTime:     1000,
		MaxMemory:      128 * 1024 * 1024,
		TestCaseId:     testCaseID,
	})
	handleResp("py3_judge", resp, err)
	fmt.Println()

	// CompileError example
	fmt.Println("CompileError example")
	resp, err = client.JudgeWithRequest(&judge.JudgeRequest{
		Src:            "this bad code",
		LanguageConfig: &javaCfg,
		MaxCpuTime:     1000,
		MaxMemory:      256 * 1024 * 1024,
		TestCaseId:     testCaseID,
	})
	if err != nil {
		fmt.Printf("compile example client error: %v\n", err)
	} else if resp != nil && resp.Err() != nil {
		fmt.Printf("compile example server error: %v\n", resp.Err())
		fmt.Println(resp.StringData())
	} else if resp != nil {
		fmt.Println(resp.StringData())
	}
}

func getenv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func handleResp(tag string, resp *judge.Resp, err error) {
	if err != nil {
		fmt.Printf("%s client error: %v\n", tag, err)
		return
	}
	if resp == nil {
		fmt.Printf("%s no response\n", tag)
		return
	}
	if resp.Err() != nil {
		fmt.Printf("%s server error: %v\n", tag, resp.Err())
		if s := resp.StringData(); s != "" {
			fmt.Println(s)
		}
		return
	}
	slice := resp.SliceData()
	fmt.Print("[\n")
	for _, item := range slice {
		fmt.Printf("\t%#v,\n", item)
	}
	fmt.Print("]\n")
}
