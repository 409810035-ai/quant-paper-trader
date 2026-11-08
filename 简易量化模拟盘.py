# -*- coding: utf-8 -*-
"""
简易量化模拟盘 - 真正一键启动版
双击 start.bat 即可运行，会弹出窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
from datetime import datetime

# 尝试导入依赖
try:
    import akshare as ak
    import pandas as pd
except ImportError:
    pass  # 启动时会处理


# ==================== 默认配置 ====================
DEFAULT_SYMBOL = "600519"
DEFAULT_NAME = "贵州茅台"
DEFAULT_SHORT = 5
DEFAULT_LONG = 20
DEFAULT_CASH = 100000


class QuantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简易量化模拟盘 - 双均线策略")
        self.root.geometry("720x580")
        self.root.resizable(False, False)

        # 样式
        style = ttk.Style()
        style.configure("TButton", font=("微软雅黑", 11))
        style.configure("TLabel", font=("微软雅黑", 10))
        style.configure("Title.TLabel", font=("微软雅黑", 14, "bold"))

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title = ttk.Label(self.root, text="🚀 简易量化模拟盘（模拟交易）", style="Title.TLabel")
        title.pack(pady=12)

        # 参数区
        frame = ttk.LabelFrame(self.root, text="参数设置（改完点开始）", padding=10)
        frame.pack(padx=15, pady=5, fill="x")

        # 第一行
        row1 = ttk.Frame(frame)
        row1.pack(fill="x", pady=3)
        ttk.Label(row1, text="股票代码:").pack(side="left")
        self.symbol_var = tk.StringVar(value=DEFAULT_SYMBOL)
        ttk.Entry(row1, textvariable=self.symbol_var, width=10).pack(side="left", padx=5)
        ttk.Label(row1, text="名称:").pack(side="left", padx=(15,0))
        self.name_var = tk.StringVar(value=DEFAULT_NAME)
        ttk.Entry(row1, textvariable=self.name_var, width=12).pack(side="left", padx=5)

        # 第二行
        row2 = ttk.Frame(frame)
        row2.pack(fill="x", pady=3)
        ttk.Label(row2, text="短期均线:").pack(side="left")
        self.short_var = tk.StringVar(value=str(DEFAULT_SHORT))
        ttk.Entry(row2, textvariable=self.short_var, width=6).pack(side="left", padx=5)
        ttk.Label(row2, text="长期均线:").pack(side="left", padx=(15,0))
        self.long_var = tk.StringVar(value=str(DEFAULT_LONG))
        ttk.Entry(row2, textvariable=self.long_var, width=6).pack(side="left", padx=5)
        ttk.Label(row2, text="初始资金:").pack(side="left", padx=(15,0))
        self.cash_var = tk.StringVar(value=str(DEFAULT_CASH))
        ttk.Entry(row2, textvariable=self.cash_var, width=10).pack(side="left", padx=5)

        # 按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=8)
        self.start_btn = ttk.Button(btn_frame, text="▶ 开始模拟交易", command=self.start_sim, width=20)
        self.start_btn.pack(side="left", padx=8)
        ttk.Button(btn_frame, text="清空日志", command=self.clear_log, width=12).pack(side="left", padx=8)

        # 日志区
        log_frame = ttk.LabelFrame(self.root, text="运行日志 / 交易记录", padding=5)
        log_frame.pack(padx=15, pady=5, fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(log_frame, height=18, font=("Consolas", 9), wrap=tk.WORD)
        self.log.pack(fill="both", expand=True)

        # 底部提示
        tip = ttk.Label(self.root, text="提示：默认模拟贵州茅台 2024年至今的双均线策略，结果仅供学习", foreground="gray")
        tip.pack(pady=5)

        self.log_msg("欢迎使用简易量化模拟盘！\n点击【开始模拟交易】即可运行。\n")

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    def clear_log(self):
        self.log.delete(1.0, tk.END)

    def start_sim(self):
        self.start_btn.config(state="disabled")
        self.clear_log()
        threading.Thread(target=self.run_strategy, daemon=True).start()

    def run_strategy(self):
        try:
            symbol = self.symbol_var.get().strip()
            name = self.name_var.get().strip()
            short = int(self.short_var.get())
            long = int(self.long_var.get())
            cash0 = float(self.cash_var.get())

            self.log_msg(f"【开始】股票：{name}({symbol})  均线：{short}/{long}  资金：{cash0:,.0f}")
            self.log_msg("-" * 50)

            # 检查依赖
            try:
                import akshare as ak
                import pandas as pd
            except ImportError:
                self.log_msg("❌ 缺少依赖库，正在尝试自动安装...")
                os.system("pip install akshare pandas -q")
                import akshare as ak
                import pandas as pd
                self.log_msg("✅ 依赖安装完成")

            # 获取数据
            self.log_msg("正在获取行情数据，请稍候...")
            end = datetime.now().strftime("%Y%m%d")
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date="20240101",
                end_date=end,
                adjust="qfq"
            )

            if df is None or df.empty:
                self.log_msg("❌ 获取数据失败，请检查股票代码是否正确，或网络是否正常。")
                self.start_btn.config(state="normal")
                return

            df = df.rename(columns={"日期": "date", "收盘": "close", "开盘": "open"})
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            self.log_msg(f"✅ 成功获取 {len(df)} 条日线数据（{df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}）")

            # 计算均线与信号
            df["ma_s"] = df["close"].rolling(short, min_periods=1).mean()
            df["ma_l"] = df["close"].rolling(long, min_periods=1).mean()
            df["signal"] = 0
            golden = (df["ma_s"].shift(1) <= df["ma_l"].shift(1)) & (df["ma_s"] > df["ma_l"])
            death = (df["ma_s"].shift(1) >= df["ma_l"].shift(1)) & (df["ma_s"] < df["ma_l"])
            df.loc[golden, "signal"] = 1
            df.loc[death, "signal"] = -1

            # 模拟交易
            cash = cash0
            pos = 0
            trades = 0
            self.log_msg("\n开始模拟交易...")

            for _, row in df.iterrows():
                price = row["close"]
                date = row["date"].strftime("%Y-%m-%d")
                sig = row["signal"]

                if sig == 1 and pos == 0 and cash > price:
                    shares = int(cash // (price * 1.0003))
                    if shares > 0:
                        cost = shares * price
                        fee = cost * 0.0003
                        cash -= cost + fee
                        pos = shares
                        trades += 1
                        self.log_msg(f"🟢 {date} 买入 {shares}股 @ {price:.2f}  剩余现金 {cash:,.0f}")

                elif sig == -1 and pos > 0:
                    revenue = pos * price
                    fee = revenue * 0.0003
                    cash += revenue - fee
                    self.log_msg(f"🔴 {date} 卖出 {pos}股 @ {price:.2f}  现金 {cash:,.0f}")
                    pos = 0
                    trades += 1

            # 最终结果
            final_price = df.iloc[-1]["close"]
            final_equity = cash + pos * final_price
            ret = (final_equity - cash0) / cash0 * 100
            buy_hold = (final_price / df.iloc[0]["close"] - 1) * 100

            self.log_msg("\n" + "=" * 45)
            self.log_msg(f"📊 模拟结果 - {name}({symbol})")
            self.log_msg("=" * 45)
            self.log_msg(f"初始资金：  {cash0:,.2f} 元")
            self.log_msg(f"最终权益：  {final_equity:,.2f} 元")
            self.log_msg(f"策略收益：  {ret:+.2f}%")
            self.log_msg(f"买入持有：  {buy_hold:+.2f}%")
            self.log_msg(f"交易次数：  {trades} 次")
            self.log_msg(f"当前持仓：  {pos} 股")
            self.log_msg("=" * 45)
            self.log_msg("\n✅ 模拟完成！这只是历史回测，不代表未来收益。")

        except Exception as e:
            self.log_msg(f"\n❌ 出错了：{str(e)}")
            self.log_msg("常见原因：网络问题 / 股票代码错误 / 依赖未装好")
        finally:
            self.start_btn.config(state="normal")


def main():
    root = tk.Tk()
    app = QuantApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
