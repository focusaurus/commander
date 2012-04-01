from Tkinter import *
from commander import command, interpret

class Application(Frame):
    def createWidgets(self):
        self.input = StringVar()
        self.prompt = Entry(self, width=100, takefocus=True,
                textvariable=self.input)
        self.prompt.bind("<Return>", self.run)
        self.prompt.pack({"anchor": "n"})
        self.prompt.focus_set()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack()

    def run(self, *args):
        interpret(self.input.get())
        self.input.set("")
        #self.quit()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


@command
def gui():
    root = Tk()
    root.title("Commander")
    app = Application(master=root)
    app.mainloop()
    root.destroy()
