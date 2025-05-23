#!/bin/bash

# Discounted Cash Flow (DCF) 计算脚本（修正版）
# 输入：每股收益、净资产、国债收益率
# 输出：30年期折现现金流估值

# 读取用户输入
read -p "Enter Earnings Per Share (EPS): " eps
read -p "Enter Book Value per share: " book_value
read -p "Enter 1-Year US Treasury Yield (%): " treasury_yield

# 转换收益率为小数
r=$(echo "scale=10; $treasury_yield / 100" | bc -l)

# 计算年金现值因子（每年折现相加）
pv_factor=0
for ((t=1; t<=30; t++))
do
	  denominator=$(echo "scale=10; (1 + $r)^$t" | bc -l)
	    term=$(echo "scale=10; 1 / $denominator" | bc -l)
	      pv_factor=$(echo "scale=10; $pv_factor + $term" | bc -l)
      done

      # 计算未来收益现值
      eps_present_value=$(echo "scale=10; $eps * $pv_factor" | bc -l)

      # 计算总DCF价值（净资产 + 收益现值）
      dcf_value=$(echo "scale=2; $book_value + $eps_present_value" | bc -l)

      # 输出结果
      echo "-------------------------"
      echo "30-Year DCF Valuation Result"
      echo "-------------------------"
      echo "EPS输入的每股收益: $eps"
      echo "每股净资产: $book_value"
      echo "国债收益率: $treasury_yield%"
      echo "年金现值因子: $pv_factor"
      echo "折现后的DCF价值: $dcf_value"
