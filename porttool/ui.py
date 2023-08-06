from tkinter import (
    ttk,
    Toplevel,
    scrolledtext,
    StringVar,
    BooleanVar,
    Canvas,
)
from tkinter.filedialog import askopenfilename
from os import getcwd
from pathlib import Path
from multiprocessing.dummy import DummyProcess
from .configs import *
from .utils import portutils

class FileChooser(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("请选择底包的boot, system和要移植的zip卡刷包")
        
        self.portzip = StringVar()
        self.basesys = StringVar()
        self.baseboot = StringVar()
        
        basesys = Path("base/system.img")
        baseboot = Path("base/boot.img")
        if basesys.exists():
            self.basesys.set(basesys.absolute())
        if baseboot.exists():
            self.baseboot.set(baseboot.absolute())

        self.frame = []
        self.__setup_widgets()
        self.focus()
    
    def __setup_widgets(self):
        def __match(val) -> str:
            match val:
                case 0: return "移植包路径"
                case 1: return "此设备boot镜像"
                case 2: return "此设备system镜像"
                case _: return ""
        def __choose_file(val: StringVar):
            val.set(askopenfilename(initialdir=getcwd()))
            self.focus()
        
        for index, current in enumerate([self.portzip, self.baseboot, self.basesys]):
            frame = ttk.Frame(self)
            label = ttk.Label(frame, text=__match(index), width=16)
            entry = ttk.Entry(frame, textvariable=current, width=40)
            button = ttk.Button(frame, text="选择文件", command=lambda x=current: __choose_file(x))
            self.frame.append([frame, label, entry, button])
        for i in self.frame:
            for index, widget in enumerate(i):
                if index == 0: # frame
                    widget.pack(side='top', fill='x', padx=5, pady=5)
                    continue
                if index == 2: # entry
                    widget.pack(side='left', fill='x', padx=5, pady=5)
                    continue
                widget.pack(side='left', padx=5, pady=5)
        bottomframe = ttk.Frame(self)
        bottombutton = ttk.Button(bottomframe, text='确定', command=self.destroy)
        bottombutton.pack(side='right', padx=5, pady=5)
        bottomframe.pack(side='bottom', fill='x', padx=5, pady=5)
    
    def get(self) -> list:
        """
        return boot.img, system.img, portzip.zip path
        """
        self.wait_window(self)
        return [
            self.baseboot.get(),
            self.basesys.get(),
            self.portzip.get(),
            ]

class LogLabel(scrolledtext.ScrolledText):
    def __init__(self, parent):
        super().__init__(parent)
        #self.vars = []

    def write(self, *vars, end='\n'):
        #self.vars = []
        for i in vars:
            self.insert('end', i)
            #self.vars.append(i)
        #self.insert('end', end)
        self.see('end')

    def flush(self): pass # have no idea how to flush on text widget

    def print(self, *vars, end='\n'):
        print(vars, end=end, file=self)

class MyUI(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="MTK 低端机移植工具")
        self.chipset_select = StringVar(value='mt65')
        self.pack_type = StringVar(value='zip')
        #self.log = LogLabel(self)
        self.item = []
        self.itembox = [] # save Checkbutton
        self.__setup_widgets()
    
    def __start_port(self):
        # item check not 0
        if self.item.__len__() == 0:
            print("Error: 移植条目为0，请先加载移植条目！", file=self.log)
            return
        files = boot, system, portzip = FileChooser(self).get()
        for i in boot, system, portzip:
            if not Path(i).exists() or i == '':
                print(f"文件{i}未选择或不存在", file=self.log)
                return
        print(f"底包boot路径为：{boot}\n"
              f"底包system镜像路径为：{system}\n"
              f"移植包路径为：{portzip}", file=self.log)
        # config items
        newdict = support_chipset_portstep[self.chipset_select.get()]
        for key, tkbool in self.item:
            newdict[key] = tkbool.get()
        
        # start to port
        p = portutils(
            newdict, *files, True if self.pack_type.get() == 'img' else False,
            self.log
        ).start
        DummyProcess(target=p).start()

    def __setup_widgets(self):
        def __scroll_event(event):
            number = int(-event.delta / 2)
            actcanvas.yview_scroll(number, 'units')
        def __scroll_func(event):
            actcanvas.configure(scrollregion=actcanvas.bbox("all"), width=300, height=180)
        
        def __create_cv_frame():
            self.actcvframe = ttk.Frame(actcanvas)
            actcanvas.create_window(0, 0, window=self.actcvframe, anchor='nw')
            self.actcvframe.bind("<Configure>", __scroll_func)
            actcanvas.update()

        def __load_port_item(select):
        
            #select = self.chipset_select.get()
            print(f"选中移植方案为{select}...", file=self.log)
            item = support_chipset_portstep[select]['flags']
            # Destory last items
            self.item = []
            self.itembox = []
            if self.actcvframe:
                self.actcvframe.destroy()
            __create_cv_frame()
            
            for index, current in enumerate(item):
                self.item.append([current, BooleanVar(value=item[current])]) # flagname, flag[True, False]
                self.itembox.append(ttk.Checkbutton(self.actcvframe, text=current, variable=self.item[index][1]))
        
            for i in self.itembox:
                i.pack(side='top', fill='x', padx=5)
        # label of support devices
        optframe = ttk.Frame(self)
        optlabel = ttk.Label(optframe)

        opttext = ttk.Label(optlabel, text="芯片类型", anchor='e')
        optmenu = ttk.OptionMenu(optlabel, self.chipset_select, support_chipset[0], *support_chipset, command=__load_port_item)

        opttext.pack(side='left', padx=5, pady=5, expand='no')
        optmenu.pack(side='left', fill='x', padx=5, pady=5, expand='no')

        optlabel.pack(side='top', fill='x')

        # Frame of support action
        actframe = ttk.Labelframe(optframe, text="支持的移植条目", height=180)
        
        actcanvas = Canvas(actframe)
        actscroll = ttk.Scrollbar(actframe, orient='vertical', command=actcanvas.yview)

        actcanvas.configure(yscrollcommand=actscroll.set)
        actcanvas.configure(scrollregion=(0, 0, 300, 180))
        actcanvas.configure(yscrollincrement=1)
        actcanvas.bind("<MouseWheel>", __scroll_event)

        actscroll.pack(side='right', fill='y')
        actcanvas.pack(side='right', fill='x', expand='yes', anchor='e')
        actframe.pack(side='top', fill='x', expand='yes')
        __create_cv_frame()

        # label of buttons
        buttonlabel = ttk.Label(optframe)
        buttonport = ttk.Button(optframe, text="一键移植", command=self.__start_port)
        buttonport.pack(side='top', fill='both', padx=5, pady=5, expand='yes')
        buttoncheck1 = ttk.Checkbutton(buttonlabel, text="输出为zip卡刷包", variable=self.pack_type, onvalue='zip', offvalue='img')
        buttoncheck2 = ttk.Checkbutton(buttonlabel, text="输出为img镜像", variable=self.pack_type, onvalue='img', offvalue='zip')

        buttoncheck1.grid(column=0, row=1, padx=5, pady=5)
        buttoncheck2.grid(column=1, row=1, padx=5, pady=5)
        buttonlabel.pack(side='top', padx=5, pady=5, fill='x', expand='yes')

        optframe.pack(side='left', padx=5, pady=5, fill='y', expand='no')
        # log label
        logframe = ttk.Labelframe(self, text="日志输出")
        self.log = LogLabel(logframe)
        self.log.pack(side='left', fill='both', anchor='center')
        logframe.pack(side='left', padx=5, pady=5, fill='both', expand='yes')
        __load_port_item(self.chipset_select.get())