from future import standard_library

standard_library.install_aliases()
from tkinter import *
from commander import engine


class Application(Frame):
    def create_widgets(self):
        self.input = StringVar()
        self.prompt = Entry(self, width=100, takefocus=True, textvariable=self.input)
        self.prompt.bind("<Return>", self.run)
        self.prompt.pack({"anchor": "n"})
        self.prompt.focus_set()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack()

    def run(self, *args):
        engine.interpret(self.input.get())
        self.input.set("")
        # self.quit()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()


@engine.command
def gui():
    root = Tk()
    root.title("Commander")
    app = Application(master=root)
    app.mainloop()
    root.destroy()
