#!/bin/bash

# 设置测试环境变量
export TESTING=1

# 运行测试
pytest tests/ -v

# 清理环境变量
unset TESTING
