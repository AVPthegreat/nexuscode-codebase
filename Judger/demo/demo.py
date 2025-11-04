import _judger
import os

if os.system("gcc main.c -o main"):
    print("compile error")
    exit(1)

ret = _judger.run(max_cpu_time=1000,
                  max_real_time=2000,
                  max_memory=128 * 1024 * 1024,
                  max_process_number=200,
                  max_output_size=10000,
                  max_stack=32 * 1024 * 1024,
                  exe_path="main",
                  input_path="1.in",
                  output_path="1.out",
                  error_path="1.out",
                  args=[],
                  env=[],
                  log_path="judger.log",
                  seccomp_rule_name="c_cpp",
                  uid=0,
                  gid=0)
print(ret)
