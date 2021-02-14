import tkinter as tk

root = tk.Tk()

root.wm_attributes("-alpha", 0.4)        # 透明度(0.0~1.0)
root.wm_attributes("-toolwindow", True)  # 置为工具窗口(没有最大最小按钮)
root.wm_attributes("-topmost", True)     # 永远处于顶层

# 还可以调用如下方法去除窗口边框
# root.overrideredirect(True)
root.mainloop()