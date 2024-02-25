import tkinter as tk
from .frames import TokenFrame, CheckInfoFrame, OtherInfoFrame, SubmitInfoFrame

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Product Extractor")

        # Create and pack the frame
        self.frame = tk.Frame(self)
        self.create_frames()
        
    # Internal frames
    def create_frames(self):
        token_info_frame = TokenFrame(self, text= "Token info")
        token_info_frame.grid(row=0, column=0, padx=60, pady=10)
        
        check_info_frame = CheckInfoFrame(self, text= "Perform checks on the brand",
                                          token_info_frame=token_info_frame)
        check_info_frame.grid(row=1, column=0, padx=50, pady=10)
        
        other_info_frame = OtherInfoFrame(self, text= "Other inputs")
        other_info_frame.grid(row=2, column=0, padx=50, pady=10)

        submit_info_frame = SubmitInfoFrame(self, text= "Generate", 
                                            token_info_frame=token_info_frame,
                                            check_info_frame=check_info_frame,
                                            other_info_frame=other_info_frame)
        submit_info_frame.grid(row=3, column=0, padx=50, pady=10)