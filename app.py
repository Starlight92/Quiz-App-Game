import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import re
class FlashcardQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Quiz Game")
        self.root.geometry("800x500")
        self.root.configure(bg="#40E0D0")
        self.root.state("zoomed")
        self.database_name = "quiz_game.db"
        self.current_field = None
        self.current_questions = []
        self.current_question = None
        self.score = 0
        self.user_name = ""
        self.user_email = ""
        self.count = 1
        self.timer_id = None  # Store the ID of the scheduled timer
        self.create_signup_screen()

    def fetch_questions(self, field):
        fields = {
            'gk': 'gk_questions',
            'grammer': 'grammer_questions',
            'sports': 'sport_questions',
            'math': 'math_questions',
            'poetry': 'poetry_questions',
            'technology': 'technology_questions'
        }

        table_name = fields.get(field)
        conn = sqlite3.connect('app_data.sqlite')
        cursor = conn.cursor()
        cursor.execute(f"SELECT question_text, answer, option1, option2, option3, option4 FROM {table_name}")
        questions = cursor.fetchall()
        conn.close()
        return questions

    def create_signup_screen(self):
        """Create a signup screen for user details."""
        self.clear_screen()

        signup_frame = tk.Frame(self.root, bg="#ECDCD5", padx=20, pady=20, relief="groove", bd=0,highlightbackground="#FF7F50",
        highlightthickness=2, width=80, height=500)
        signup_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(signup_frame, text="Sign Up", font=("Arial", 28, "bold"), bg="#ECDCD5", fg="black").pack(pady=10)
        tk.Label(signup_frame, text="Enter your name:", font=("Arial", 18), bg="#ECDCD5", fg="black").pack(pady=5)
        self.name_entry = tk.Entry(signup_frame, font=("Arial", 16), width=20)
        self.name_entry.pack(pady=5)

        tk.Label(signup_frame, text="Enter your email:", font=("Arial", 18), bg="#ECDCD5", fg="black").pack(pady=5)
        self.email_entry = tk.Entry(signup_frame, font=("Arial", 16), width=20)
        self.email_entry.pack(pady=5)

        tk.Button(
            signup_frame,
            text="Submit",
            font=("Arial", 14),
            bg="#40E0D0",
            fg="black",
            width=15,
            command=self.save_user_info,
        ).pack(pady=20)

    def save_user_info(self):
        """Save user info and go to the home screen."""
        self.user_name = self.name_entry.get().strip()
        self.user_email = self.email_entry.get().strip()

        # Validate name and email
        if not self.user_name or not self.user_email:
            messagebox.showerror("Error", "Please fill out all fields!")
            return

        if not self.is_valid_name(self.user_name):
            messagebox.showerror("Error", "Name should only contain letters and spaces!")
            return

        if not self.is_valid_email(self.user_email):
            messagebox.showerror("Error", "Please enter a valid email address!")
            return

        # Check if the user already exists in the database
        conn = sqlite3.connect('app_data.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_gmail = ?", (self.user_email,))
        existing_user = cursor.fetchone()

        if existing_user:
            # User already exists, skip insertion
            messagebox.showinfo("Welcome Back!", f"Welcome back, {self.user_name}!")
        else:
            # Save the user information to the database if they don't exist
            cursor.execute("INSERT INTO user (user_name, user_gmail) VALUES (?, ?)", (self.user_name, self.user_email))
            conn.commit()
            messagebox.showinfo("Welcome!", f"Welcome, {self.user_name}!")

        conn.close()
        self.create_home_screen()

    def is_valid_name(self, name):
        """Check if the name contains only alphabets and spaces."""
        return name.replace(" ", "").isalpha()

    def is_valid_email(self, email):
        """Check if the email follows a valid pattern."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None

    def create_home_screen(self):
        """Create the home screen where users select the quiz field."""
        self.clear_screen()

        home_frame = tk.Frame(self.root, bg="#ECDCD5", padx=10, pady=10, relief="groove", bd=5)
        home_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(home_frame, text=f"Welcome, {self.user_name}!", font=("Arial", 24, "bold"), bg="#ECDCD5", fg="black").grid(row=0, column=0, columnspan=3, pady=20)

        tk.Label(home_frame, text="Choose a Field:", font=("Arial", 16), bg="#ECDCD5", fg="black").grid(row=1, column=0, columnspan=3, pady=10)

        fields = ["GK", "Grammer", "Sports", "Math", "Poetry", "Technology"]

        for i, field in enumerate(fields):
            row = (i // 3) + 2
            column = i % 3

            tk.Button(
                home_frame,
                text=field,
                font=("Arial", 14),
                bg="#40E0D0",
                fg="black",
                width=15,
                height=2,
                command=lambda f=field.lower(): self.start_quiz(f),
            ).grid(row=row, column=column, padx=10, pady=10)

    def start_quiz(self, field):
        """Start the quiz for the selected field."""
        self.current_field = field
        self.current_questions = self.fetch_questions(field)
        self.score = 0
        self.ask_question()

    def ask_question(self):
        """Display a question for the user to answer."""
        self.clear_screen()

        # Cancel any existing timer if exists
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        question_frame = tk.Frame(self.root, bg="#ECDCD5", padx=50, pady=50, relief="groove",  bd=0,highlightbackground="#FF7F50",
        highlightthickness=2, width=50)
        question_frame.place(relx=0.5, rely=0.5, anchor="center")

        if len(self.current_questions) == 0:  # No questions left
            self.show_results()
            return

        question_data = random.choice(self.current_questions)
        self.current_questions.remove(question_data)

        self.current_question = {
            "question": question_data[0],
            "answer": question_data[1],
            "options": question_data[2:],
        }

        tk.Label(question_frame, text=f"Field: {self.current_field}", font=("Arial", 16), bg="#ECDCD5", fg="black").pack(pady=10)
        tk.Label(question_frame, text=f"Score: {self.score}", font=("Arial", 14), bg="#ECDCD5", fg="black").pack(pady=5)
        tk.Label(question_frame, text=f"Q{self.count}: {self.current_question['question']}", font=("Arial", 14), wraplength=500, bg="#ECDCD5", fg="black").pack(pady=20)
        self.count += 1
        self.selected_option = tk.StringVar(value="")
        for option in self.current_question["options"]:
            tk.Radiobutton(
                question_frame,
                text=option,
                variable=self.selected_option,
                value=option,
                font=("Arial", 14),
                bg="#ECDCD5",
                fg="black",
                selectcolor="white",
            ).pack(anchor="w", padx=20, pady=5)

        self.timer_label = tk.Label(question_frame, text="Time Left: 30s", font=("Arial", 14), bg="#ECDCD5", fg="black")
        self.timer_label.pack(pady=10)

        self.time_left = 30  # Reset the timer for this question
        self.update_timer()

        tk.Button(
            question_frame,
            text="Submit Answer",
            font=("Arial", 14),
            bg="#40E0D0",
            fg="black",
            width=15,bd=0,highlightbackground="#FF7F50",
        highlightthickness=2,
            command=self.check_answer,
        ).pack(pady=10)

    def update_timer(self):
        """Update the countdown timer."""
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"Time Left: {self.time_left}s")
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.timer_id = None  # Clear the timer ID when time runs out
            self.ask_question()  # Proceed with the next question

    def check_answer(self):
        """Check if the selected answer is correct and move to the next question."""
        user_answer = self.selected_option.get()

        if not user_answer:
            messagebox.showwarning("No Answer", "Please select an option before proceeding.")
            return

        correct_answer = self.current_question["answer"]

        if user_answer == correct_answer:
            self.score += 1

        self.ask_question()

    def show_results(self):
        """Display the final result after the quiz."""
        self.clear_screen()

        # Fetch total questions for the selected field
        total_questions = len(self.fetch_questions(self.current_field))
        percentage = (self.score / total_questions) * 100 if total_questions > 0 else 0

        # Determine a motivational message
        if percentage == 100:
            message = "Outstanding! Perfect Score! 🎉"
        elif percentage >= 75:
            message = "Great job! You're really good at this! 👍"
        elif percentage >= 50:
            message = "Good effort! Keep practicing! 🙂"
        else:
            message = "Don't give up! You'll get better with more practice. 💪"

        # Result screen layout
        result_frame = tk.Frame(self.root, bg="#ECDCD5", padx=35, pady=35, relief="groove", bd=0,highlightbackground="#FF7F50",
        highlightthickness=2,)
        result_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(result_frame, text="Quiz Complete!", font=("Arial", 18, "bold"), bg="#ECDCD5", fg="black").pack(pady=10)
        tk.Label(result_frame, text=f"Your Final Score: {self.score} / {total_questions}", font=("Arial", 16), bg="#ECDCD5", fg="black").pack(pady=10)
        tk.Label(result_frame, text=f"Percentage: {percentage:.2f}%", font=("Arial", 16), bg="#ECDCD5", fg="black").pack(pady=10)
        tk.Label(result_frame, text=message, font=("Arial", 14), bg="#ECDCD5", fg="black").pack(pady=20)

        tk.Button(
            result_frame,
            text="Another Quiz",
            font=("Arial", 14),
            bg="#40E0D0",
            fg="black",
            width=15,
            command=self.create_home_screen,
        ).pack(pady=20)

        tk.Button(
            result_frame,
            text="Quit Game",
            font=("Arial", 14),
            bg="#40E0D0",  # Red color for the quit button
            fg="black",
            width=15,
            command=self.quit_game,  # Call the quit_game method when clicked
        ).pack(pady=10)

    def clear_screen(self):
        """Clear the current screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def quit_game(self):
        """Quit the game and close the application."""
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardQuizApp(root)
    root.mainloop()
