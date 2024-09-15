import threading

import customtkinter as ctk
from llama_server import invoke_stream, check_server_running
from tray_icon import TrayIcon
from utils import load_config, notify


class Screen:
    def __init__(self):
        self.config = load_config()
        self.last_response = ""
        self.context = None
        self.janela = None
        self.send_notify = False
        self.tray_icon = TrayIcon(self)

    def update_context(self, new_context):
        self.context = new_context
        self.label_context.configure(
            text=self.config["screen"]["msg_context"]["selected"],
            text_color="green",
        )
        self.btn_delete_context.configure(state="normal")

    def get_llama_response(self, user_input):
        initial_response = f"USER: {user_input}\n\nAI: "
        self.janela.after(0, self.update_response, initial_response, False)

        for chunk in invoke_stream(prompt=user_input, context=self.context):
            self.janela.after(0, self.update_response, chunk, False)
            self.last_response = self.last_response + chunk

        self.janela.after(0, self.update_response, "\n\n", True)

    def update_response(self, response_chunk, is_final):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", response_chunk)
        self.output_textbox.configure(state="disabled")

        self.output_textbox.see("end")

        if is_final:
            self.input_textbox.delete("1.0", "end")
            self.btn_copiar.configure(state="normal")

    def on_closing(self):
        self.janela.withdraw()
        self.tray_icon.show_tray_icon()
        if not self.send_notify:
            notify("Executando em segundo plano")
            self.send_notify = True

    #########################
    # Actions buttons
    #########################
    def iniciar(self):
        user_input = self.input_textbox.get("1.0", "end-1c")
        if user_input.strip() == "":
            return

        threading.Thread(target=self.get_llama_response, args=(user_input,)).start()

    def copiar(self):
        if self.last_response:
            self.janela.clipboard_clear()
            self.janela.clipboard_append(self.last_response)
            self.janela.update()

    def limpar_contexto(self):
        self.context = None
        self.label_context.configure(
            text=self.config["screen"]["msg_context"]["default"],
            text_color="white",
        )
        self.btn_delete_context.configure(state="disabled")

    def run(self):
        #########################
        # Config Screen
        #########################
        self.janela = ctk.CTk()
        self.janela.title(self.config["app_title"])

        # makes it in the center of the screen
        screen_width = self.janela.winfo_screenwidth()
        screen_height = self.janela.winfo_screenheight()
        window_width = self.config["screen"]["window"]["width"]
        window_height = self.config["screen"]["window"]["height"]
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.janela.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # self.janela.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.janela.protocol("WM_DELETE_WINDOW", self.janela.quit())

        self.janela.attributes("-topmost", True)
        self.janela.update()

        #########################
        # Title app
        #########################
        frame_button = ctk.CTkFrame(self.janela, fg_color="transparent")
        frame_button.pack(padx=10, pady=10)

        self.label_model = ctk.CTkLabel(
            frame_button,
            text="🔴   ",
            font=("arial bold", 18),
            text_color="red",
            bg_color=self.janela.cget("bg"),
        )
        self.label_model.pack(side="left")

        ctk.CTkLabel(
            frame_button,
            text=self.config["app_title"],
            font=("arial bold", 20),
        ).pack(side="left")

        threading.Thread(target=check_server_running, args=(self.label_model,)).start()

        #########################
        # Mensage context
        #########################
        self.label_context = ctk.CTkLabel(
            self.janela,
            text=self.config["screen"]["msg_context"]["default"],
            font=("arial", 12),
            bg_color=self.janela.cget("bg"),
        )
        self.label_context.pack()

        #########################
        # Output
        #########################
        self.output_textbox = ctk.CTkTextbox(
            self.janela,
            font=("arial", 14),
            height=140,
            corner_radius=15,
            activate_scrollbars=True,
            state="disabled",
        )
        self.output_textbox.pack(fill="both", expand=True, padx=30, pady=5)

        #########################
        # Input
        #########################
        self.input_textbox = ctk.CTkTextbox(
            self.janela,
            font=("arial", 14),
            height=80,
            corner_radius=15,
            activate_scrollbars=True,
            bg_color=self.janela.cget("bg"),
        )
        self.input_textbox.pack(fill="both", padx=30)

        #########################
        # Buttons
        #########################
        frame_button = ctk.CTkFrame(self.janela)
        frame_button.pack(pady=10, padx=10)

        ctk.CTkButton(
            frame_button,
            text="Iniciar",
            font=("arial bold", 15),
            command=self.iniciar,
        ).pack(side="left", padx=5)

        self.btn_copiar = ctk.CTkButton(
            frame_button,
            text="Copiar",
            font=("arial bold", 15),
            command=self.copiar,
            state="disabled",
        )
        self.btn_copiar.pack(side="left", padx=5)

        self.btn_delete_context = ctk.CTkButton(
            frame_button,
            text="Limpar contexto",
            font=("arial bold", 15),
            command=self.limpar_contexto,
            state="disabled",
        )
        self.btn_delete_context.pack(side="left", padx=5)

        #########################
        # Run Screen
        #########################
        self.janela.mainloop()
