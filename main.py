import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import filedialog
from urllib.parse import urlparse
import random
from tkinter import messagebox
import pickle
import os
import heapq


class MainWindow(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(width=400, height=400)
        self.title("Kare Puzzle")
        self.iconbitmap("puzzle.ico")
        self.frame = ttk.Frame(
            self,
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.puzzle_image = ImageTk.PhotoImage(
            Image.open("puzzle.png").resize((100, 100)))
        self.puzzle_image_label = ttk.Label(
            self.frame, image=self.puzzle_image)
        self.puzzle_image_label.pack(pady=10)

        self.name_label = ttk.Label(
            self.frame, text="Kare Puzzle Oyunu", font=("Segoe UI", 25, "bold"))
        self.name_label.pack(pady=10)

        self.game_button = ttk.Button(
            self.frame,
            text="Oyuna Başla",
            command=self.open_game_window,
            padding=[20, 20, 20, 20]
        )
        self.game_button.pack(pady=10)

        self.top_scores_button = ttk.Button(
            self.frame,
            text="En Yüksek Skorlar",
            command=self.open_top_scores,
            padding=[20, 20, 20, 20]
        )
        self.top_scores_button.pack(pady=10)

    def open_game_window(self):
        if not GameWindow.alive:
            self.withdraw()
            self.game_window = GameWindow()

    def open_top_scores(self):
        if not TopScores.alive:
            self.withdraw()
            self.top_scores_window = TopScores()


class TopScores(tk.Toplevel):
    alive = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.config(width=500, height=500)
        self.title("En Yüksek Skorlar")
        self.geometry("500x800")
        self.iconbitmap("puzzle.ico")

        self.frame = ttk.Frame(
            self,
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")
        self.name_label = ttk.Label(
            self.frame, text="En Yüksek 10 Skor", font=("Segoe UI", 25, "bold"))
        self.name_label.pack(pady=10)
        self.top_scores_frame = self.frame = ttk.Frame(
            self.frame,
        )
        self.top_scores_frame.pack(pady=10)
        self.scores_dict_list = []
        if os.path.isfile("skorlar.txt"):
            with open('skorlar.txt', 'rb') as f:
                while True:
                    try:
                        my_dict = pickle.load(f)

                        self.scores_dict_list.append(my_dict)
                    except EOFError:
                        break
            f.close()

        tk.Label(self.top_scores_frame, text='Sıra', font=(
            "Segoe UI", 20, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(self.top_scores_frame, text='Ad', font=(
            "Segoe UI", 20, "bold")).grid(row=0, column=1, padx=5)
        tk.Label(self.top_scores_frame, text='Hamle', font=(
            "Segoe UI", 20, "bold")).grid(row=0, column=2, padx=5)
        tk.Label(self.top_scores_frame, text='Skor', font=(
            "Segoe UI", 20, "bold")).grid(row=0, column=3, padx=5)
        top_ten_scores = heapq.nlargest(
            10, self.scores_dict_list, key=lambda x: x['score'])
        for i in range(len(top_ten_scores)):
            col = 0
            tk.Label(self.top_scores_frame, text=f"#{i+1}", font=(
                "Segoe UI", 18, "bold")).grid(row=i+1, column=col)
            for key in top_ten_scores[i]:
                col += 1
                tk.Label(self.top_scores_frame, text=f"{top_ten_scores[i][key]}", font=(
                    "Segoe UI", 18, "bold")).grid(row=i+1, column=col)

        self.__class__.alive = True

    def destroy(self):
        self.__class__.alive = False
        main_window.deiconify()
        return super().destroy()


class GameWindow(tk.Toplevel):

    alive = False

    image_username_frame = None
    game_info_frame = None
    puzzle_frame = None
    shuffle_frame = None

    image_path_label = None
    image_path = ""

    image_url = None
    image_url_entry = None
    image_url_entry_label = None

    name = None
    name_entry = None
    name_entry_label = None

    shuffle_puzzle_button = None

    puzzle_pieces_linked_list = None

    first_selected_puzzle_piece_number = None

    score = 0

    top_score = 0

    moves = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.config(width=500, height=500)
        self.title("Oyun")
        self.geometry("900x950")
        self.iconbitmap("puzzle.ico")

        self.puzzle_pieces_linked_list = LinkedList()

        self.image_username_frame = ttk.Frame(self)
        self.game_info_frame = ttk.Frame(self)
        self.puzzle_frame = ttk.Frame(self)
        self.shuffle_frame = ttk.Frame(self)

        self.image_username_frame.grid(row=0, column=0)
        self.game_info_frame.grid(row=1, column=0,pady=10)
        self.puzzle_frame.grid(row=2, column=0,pady=10)
        self.shuffle_frame.grid(row=3, column=0,pady=10)

        self.image_info = ttk.Label(
                self.image_username_frame, text="Bilgisayarınızdan bir görsel seçebilir veya görselin linkini girebilirsiniz.", font=("Segoe UI", 18, "bold"),padding=[40, 0, 40, 0])
        self.image_info.grid(row=0, column=0,columnspan=4)

        self.image_pick_button = ttk.Button(
            self.image_username_frame,
            text="Görsel Seç",
            command=self.pick_image
        )
        self.image_pick_button.grid(
            row=1, column=0,pady=10, columnspan=1)

        self.image_url_entry_label = ttk.Label(
            self.image_username_frame, text="Görsel linkini giriniz : ")
        self.image_url_entry_label.grid(row=2, column=0, columnspan=1,pady=10)

        self.image_url = tk.StringVar(self.image_url_entry, "")
        self.image_url.trace('w', self.on_image_url_write)
        self.image_url_entry = ttk.Entry(
            self.image_username_frame, textvariable=self.image_url, width=50)
        self.image_url_entry.grid(row=2, column=1, columnspan=3,pady=10)

        self.focus()

        self.__class__.alive = True

    def destroy(self):

        self.__class__.alive = False
        main_window.deiconify()
        return super().destroy()

    def pick_image(self):
        image_path = filedialog.askopenfilename(initialdir="/", title="Bir Görsel Seçin", filetypes=[
                                                ("PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("ICON", "*.ico")])

        self.image_path = image_path

        if self.image_path_label is None:
            self.image_path_label = ttk.Label(
                self.image_username_frame, text=f"Görsel Adresi : {self.image_path}", font=("Segoe UI", 14, "bold"))
            self.image_path_label.grid(row=1, column=1, columnspan=3)

        if self.image_path != "":
            self.image_url_entry.config(state=tk.DISABLED)
            self.image_url.set("")
            self.image_path_label.config(
                text=f"Görsel Adresi : {self.image_path}")
            self.create_puzzle()
        else:
            self.image_url_entry.config(state=tk.NORMAL)
            self.image_path = ""
            self.image_path_label.destroy()
            self.image_path_label = None
            self.clear_puzzle_frame()
            if(self.shuffle_puzzle_button != None):
                self.shuffle_puzzle_button.destroy()
                self.shuffle_puzzle_button = None

        self.create_or_destroy_name_entry()

    def on_image_url_write(self, *args):
        if self.image_url.get() != "":
            self.image_path = ""
            self.image_pick_button.config(state=tk.DISABLED)

            if(self.is_valid_url(self.image_url.get())):
                self.create_puzzle()
        else:
            self.image_pick_button.config(state=tk.NORMAL)
            self.clear_puzzle_frame()
            if(self.shuffle_puzzle_button != None):
                self.shuffle_puzzle_button.destroy()
                self.shuffle_puzzle_button = None

        self.create_or_destroy_name_entry()

    def create_or_destroy_name_entry(self):
        if (self.image_path != "" or (self.is_valid_url(self.image_url.get()) and self.image_url.get() != "")) and self.name_entry == None:
            self.name_entry_label = ttk.Label(
                self.image_username_frame, text="Kullanıcı adını giriniz : ")
            self.name_entry_label.grid(row=3, column=0, columnspan=1)

            self.name = tk.StringVar(self.name_entry, "Örnek")
            self.name_entry = ttk.Entry(
                self.image_username_frame, textvariable=self.name, width=50)
            self.name_entry.grid(row=3, column=1, columnspan=3)

        if ((self.image_path == "" and not (self.is_valid_url(self.image_url.get()))) and self.name_entry != None):
            self.name_entry.destroy()
            self.name_entry_label.destroy()
            self.name_entry = None
            self.name_entry_label = None
            self.name.set("")

    def create_puzzle(self):
        resized_puzzle_image = None

        self.clear_puzzle_frame()

        self.puzzle_pieces_linked_list.clear()

        if(self.image_path != ""):
            image = Image.open(self.image_path).convert("RGBA")
            resized_puzzle_image = image.resize((800, 600))

        elif(self.is_valid_url(self.image_url.get())):
            response = requests.get(self.image_url.get())
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            resized_puzzle_image = image.resize((800, 600))

        if resized_puzzle_image:
            for row in range(4):
                for col in range(4):
                    x = col * 200
                    y = row * 150
                    crop = resized_puzzle_image.crop((x, y, x+200, y+150))
                    new_image = Image.new(
                        'RGBA', (200, 150), (255, 255, 255, 255))

                    new_image.paste(crop, (0, 0), crop)

                    photo = ImageTk.PhotoImage(new_image)
                    button = tk.Button(self.puzzle_frame, image=photo, command=lambda index=(4*row) + col: self.swap(index
                                                                                                                     ), borderwidth=2,relief="solid",state=tk.DISABLED)
                    button.photo = photo
                    button.row = row
                    button.col = col
                    self.puzzle_pieces_linked_list.append_node(
                        (4*row) + col, button)

                    button.grid(row=row, column=col)

        self.shuffle_puzzle_button = ttk.Button(
            self.shuffle_frame,
            text="Bulmacayı Karıştır",
            command=self.shuffle_puzzle
        )
        self.shuffle_puzzle_button.grid(row=0, column=0, columnspan=2)

    def shuffle_puzzle(self):
        self.score_label = ttk.Label(
            self.game_info_frame, text=f"Skorun : {self.score}", font=("Segoe UI", 18, "bold"))
        self.score_label.grid(row=0, column=2, columnspan=2)

        if os.path.isfile("skorlar.txt"):
            scores_dict_list = []
            with open('skorlar.txt', 'rb') as f:
                while True:
                    try:
                        my_dict = pickle.load(f)

                        scores_dict_list.append(my_dict)
                    except EOFError:
                        break
            f.close()
            highest_score_dict = max(
                scores_dict_list, key=lambda x: x['score'], default={'score': 0})
            self.top_score = highest_score_dict["score"]

        self.best_score_label = ttk.Label(
            self.game_info_frame, text=f"En Yüksek Skor : {self.top_score}", font=("Segoe UI", 18, "bold"))
        self.best_score_label.grid(row=1, column=2, columnspan=2)

        self.image_pick_button.config(state=tk.DISABLED)
        self.image_url_entry.config(state=tk.DISABLED)
        self.name_entry.config(state=tk.DISABLED)
        self.shuffle_puzzle_button.config(state=tk.DISABLED)

        self.swap_before_game()

        is_puzzle_solved = self.is_puzzle_solved()

        while is_puzzle_solved:
            self.swap_before_game()
            is_puzzle_solved = self.is_puzzle_solved()

        head = self.puzzle_pieces_linked_list.head
        while head is not None:
            head.puzzle_piece_button.config(state=tk.NORMAL)
            head = head.next

        for i in range(16):
            node = self.puzzle_pieces_linked_list.get_node(i)

            if(node.puzzle_piece_number == i):
                node.puzzle_piece_button.config(state=tk.DISABLED)

    def clear_puzzle_frame(self):
        for child in self.puzzle_frame.winfo_children():
            child.destroy()

    def clear_game_info_frame(self):
        for child in self.game_info_frame.winfo_children():
            child.destroy()

    def clear_shuffle_frame(self):
        for child in self.shuffle_frame.winfo_children():
            child.destroy()

    def swap(self, selected_puzzle_piece_number):

        if self.first_selected_puzzle_piece_number is not None and selected_puzzle_piece_number == self.first_selected_puzzle_piece_number:
            return

        if self.first_selected_puzzle_piece_number is None:
            self.first_selected_puzzle_piece_number = selected_puzzle_piece_number
        else:

            first_button_index = self.puzzle_pieces_linked_list.index_of(
                self.first_selected_puzzle_piece_number)
            second_button_index = self.puzzle_pieces_linked_list.index_of(
                selected_puzzle_piece_number)
            first_node = self.puzzle_pieces_linked_list.get_node(
                first_button_index)
            second_node = self.puzzle_pieces_linked_list.get_node(
                second_button_index)
            temp_row = first_node.puzzle_piece_button.row
            temp_col = first_node.puzzle_piece_button.col
            first_node.puzzle_piece_button.row = second_node.puzzle_piece_button.row
            first_node.puzzle_piece_button.col = second_node.puzzle_piece_button.col
            second_node.puzzle_piece_button.row = temp_row
            second_node.puzzle_piece_button.col = temp_col
            first_node.puzzle_piece_button.grid(
                row=first_node.puzzle_piece_button.row, column=first_node.puzzle_piece_button.col)
            second_node.puzzle_piece_button.grid(
                row=second_node.puzzle_piece_button.row, column=second_node.puzzle_piece_button.col)
            self.puzzle_pieces_linked_list.swap_nodes(
                first_node=first_node, second_node=second_node)

            if(self.first_selected_puzzle_piece_number == second_button_index):
                first_node.puzzle_piece_button.config(state=tk.DISABLED)
                self.score += 5
            else:
                self.score -= 10

            if(selected_puzzle_piece_number == first_button_index):
                second_node.puzzle_piece_button.config(state=tk.DISABLED)
                self.score += 5
            self.first_selected_puzzle_piece_number = None
            self.moves += 1
            self.score_label.config(text=f"Skorun : {self.score}")
            is_puzzle_solved = self.is_puzzle_solved()
            if is_puzzle_solved:
                messagebox.showinfo(f"Oyun Bitti {self.name.get()}",
                                    f"Bulmacayı {self.moves} hamlede {self.score} puan alarak tamamladınız.")

                with open('skorlar.txt', 'ab') as f:
                    skor = {'name': self.name.get(), 'moves': self.moves,
                            'score': self.score}
                    pickle.dump(skor, f)

                f.close()

                self.reset_puzzle_button = ttk.Button(
                    self.shuffle_frame,
                    text="Oyunu Sıfırla",
                    command=self.reset_game
                )
                self.reset_puzzle_button.grid(row=0, column=2, columnspan=2)

    def reset_game(self):
        self.image_pick_button.config(state=tk.NORMAL)
        self.image_path = ""
        self.image_path_label.config(text="")
        self.image_url_entry.config(state=tk.NORMAL)
        self.image_url.set("")
        self.create_or_destroy_name_entry()
        self.clear_puzzle_frame()
        self.puzzle_pieces_linked_list.clear()
        self.first_selected_puzzle_piece_number = None
        self.score = 0
        self.top_score = 0
        self.moves = 0
        self.clear_game_info_frame()
        self.clear_shuffle_frame()

    def swap_before_game(self):
        puzzle_piece_indexes = []
        for i in range(16):
            puzzle_piece_indexes.append(i)

        for i in range(50):
            first_button_node = self.puzzle_pieces_linked_list.get_node(
                random.choice(puzzle_piece_indexes))
            second_button_node = self.puzzle_pieces_linked_list.get_node(
                random.choice(puzzle_piece_indexes))
            temp_row = first_button_node.puzzle_piece_button.row
            temp_col = first_button_node.puzzle_piece_button.col
            first_button_node.puzzle_piece_button.row = second_button_node.puzzle_piece_button.row
            first_button_node.puzzle_piece_button.col = second_button_node.puzzle_piece_button.col
            second_button_node.puzzle_piece_button.row = temp_row
            second_button_node.puzzle_piece_button.col = temp_col
            first_button_node.puzzle_piece_button.grid(
                row=first_button_node.puzzle_piece_button.row, column=first_button_node.puzzle_piece_button.col)
            second_button_node.puzzle_piece_button.grid(
                row=second_button_node.puzzle_piece_button.row, column=second_button_node.puzzle_piece_button.col)
            self.puzzle_pieces_linked_list.swap_nodes(
                first_node=first_button_node, second_node=second_button_node)

    def is_puzzle_solved(self):

        for i in range(16):
            node = self.puzzle_pieces_linked_list.get_node(i)

            if(node.puzzle_piece_number != i):
                return False
        return True

    # https://stackoverflow.com/questions/7160737/how-to-validate-a-url-in-python-malformed-or-not ' dan alınmıştır.

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False


class Node:
    def __init__(self, puzzle_piece_number, puzzle_piece_button):
        self.puzzle_piece_number = puzzle_piece_number
        self.puzzle_piece_button = puzzle_piece_button
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append_node(self, puzzle_piece_number, puzzle_piece_button):
        node = Node(puzzle_piece_number, puzzle_piece_button)

        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = node

        self.size += 1

    def index_of(self, puzzle_piece_number):
        index = -1

        node = self.head

        while node:
            index += 1
            if(node.puzzle_piece_number == puzzle_piece_number):
                return index
            node = node.next

        return index

    def get_node(self, node_index):
        node = self.head

        if node_index == 0:
            return node

        while node_index:
            node_index -= 1
            if node.next is not None:
                node = node.next
            else:
                return None

        return node

    def swap_nodes(self, first_node, second_node):
        if first_node == second_node:
            return

        prev_first = None
        curr_first = self.head
        while curr_first is not None and curr_first.puzzle_piece_number != first_node.puzzle_piece_number:
            prev_first = curr_first
            curr_first = curr_first.next

        prev_second = None
        curr_second = self.head
        while curr_second is not None and curr_second.puzzle_piece_number != second_node.puzzle_piece_number:
            prev_second = curr_second
            curr_second = curr_second.next

        if curr_first is None or curr_second is None:
            return

        if prev_first is not None:
            prev_first.next = curr_second
        else:
            self.head = curr_second

        if prev_second is not None:
            prev_second.next = curr_first
        else:
            self.head = curr_first

        curr_first.next, curr_second.next = curr_second.next, curr_first.next

    def clear(self):
        self.head = None

    def is_empty(self):
        return (self.head is None)

    def list_size(self):
        return self.size


main_window = MainWindow()
main_window.mainloop()
