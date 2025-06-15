import tkinter as tk
from tkinter import messagebox
import random

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)

        # Cartoon style settings
        self.GAME_WIDTH = 600
        self.GAME_HEIGHT = 400
        self.SPACE_SIZE = 20
        self.SNAKE_LENGTH = 3
        self.difficulties = {
            "Easy": 180,
            "Normal": 140,
            "Hard": 90,
        }
        self.current_difficulty = "Easy"
        self.speed = self.difficulties[self.current_difficulty]

        # Cartoon colors
        self.BG_COLOR = "#f7e7a6"  # light yellow
        self.SNAKE_COLOR = "#4ee44e"  # bright green
        self.SNAKE_OUTLINE = "#267326"
        self.SNAKE_SPOT = "#ffe066"  # yellow spot
        self.FOOD_COLOR = "#ff3333"
        self.BONUS_FOOD_COLOR = "#ffd700"
        self.TEXT_COLOR = "#333333"

        # Main frame
        self.main_frame = tk.Frame(root, bg=self.BG_COLOR)
        self.main_frame.pack(expand=True, fill='both')

        # Score label
        self.score_label = tk.Label(
            self.main_frame,
            text="Score: 0",
            font=('Arial', 20),
            fg=self.TEXT_COLOR,
            bg=self.BG_COLOR
        )
        self.score_label.pack(pady=10)

        # Level label
        self.difficulty_label = tk.Label(
            self.main_frame,
            text=f"Level: {self.current_difficulty}",
            font=('Arial', 16),
            fg=self.TEXT_COLOR,
            bg=self.BG_COLOR
        )
        self.difficulty_label.pack()

        # Game canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.GAME_WIDTH,
            height=self.GAME_HEIGHT,
            bg=self.BG_COLOR,
            highlightthickness=2,
            highlightbackground="#bfa100"
        )
        self.canvas.pack(pady=10)

        # Buttons frame
        self.button_frame = tk.Frame(self.main_frame, bg=self.BG_COLOR)
        self.button_frame.pack(pady=10)
        for difficulty in self.difficulties.keys():
            btn = tk.Button(
                self.button_frame,
                text=difficulty,
                font=('Arial', 12),
                command=lambda d=difficulty: self.start_game(d)
            )
            btn.pack(side=tk.LEFT, padx=10)

        # Game variables
        self.direction = 'right'
        self.score = 0
        self.food_count = 0
        self.snake_positions = []
        self.food_position = []
        self.bonus_food_position = []
        self.snake_body = []
        self.bonus_food_timer = None
        self.game_active = False
        self.movement_timer = None

        # Bind keys
        self.root.bind('<Left>', lambda event: self.change_direction('left'))
        self.root.bind('<Right>', lambda event: self.change_direction('right'))
        self.root.bind('<Up>', lambda event: self.change_direction('up'))
        self.root.bind('<Down>', lambda event: self.change_direction('down'))

        self.show_start_screen()

    def show_start_screen(self):
        self.canvas.delete("all")
        self.game_active = False
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.create_text(
            self.GAME_WIDTH/2,
            self.GAME_HEIGHT/2 - 50,
            text="Welcome to Snake Game!",
            font=('Arial', 24),
            fill=self.TEXT_COLOR
        )
        self.canvas.create_text(
            self.GAME_WIDTH/2,
            self.GAME_HEIGHT/2,
            text="Select a difficulty level to start",
            font=('Arial', 16),
            fill=self.TEXT_COLOR
        )
        self.canvas.create_text(
            self.GAME_WIDTH/2,
            self.GAME_HEIGHT/2 + 50,
            text="Use arrow keys to control the snake",
            font=('Arial', 14),
            fill=self.TEXT_COLOR
        )

    def start_game(self, difficulty):
        try:
            if self.movement_timer:
                self.root.after_cancel(self.movement_timer)
                self.movement_timer = None
            if self.bonus_food_timer:
                self.root.after_cancel(self.bonus_food_timer)
                self.bonus_food_timer = None
            self.current_difficulty = difficulty
            self.speed = self.difficulties[difficulty]
            self.difficulty_label.config(text=f"Level: {difficulty}")
            self.game_active = True
            self.direction = 'right'
            self.score = 0
            self.food_count = 0
            self.snake_positions = []
            self.food_position = []
            self.bonus_food_position = []
            self.snake_body = []
            self.score_label.config(text="Score: 0")
            self.canvas.delete("all")
            for i in range(self.SNAKE_LENGTH):
                x = self.SPACE_SIZE * (self.SNAKE_LENGTH - i)
                y = self.SPACE_SIZE
                self.snake_positions.append([x, y])
                # Draw rounded body (oval)
                oval = self.canvas.create_oval(
                    x, y,
                    x + self.SPACE_SIZE, y + self.SPACE_SIZE,
                    fill=self.SNAKE_COLOR,
                    outline=self.SNAKE_OUTLINE,
                    width=2,
                    tags="snake"
                )
                # Add yellow spot to body (not head)
                if i != 0:
                    spot_size = self.SPACE_SIZE // 2
                    spot_offset = self.SPACE_SIZE // 4
                    self.canvas.create_oval(
                        x + spot_offset, y + spot_offset,
                        x + spot_offset + spot_size, y + spot_offset + spot_size,
                        fill=self.SNAKE_SPOT,
                        outline="",
                        tags="snake_spot"
                    )
                self.snake_body.append(oval)
            self.spawn_food()
            self.move_snake()
        except Exception as e:
            messagebox.showerror("Error", f"Error starting game: {str(e)}")
            self.show_start_screen()

    def move_snake(self):
        try:
            if not self.game_active:
                return
            head = self.snake_positions[0]
            if self.direction == 'right':
                new_head = [head[0] + self.SPACE_SIZE, head[1]]
            elif self.direction == 'left':
                new_head = [head[0] - self.SPACE_SIZE, head[1]]
            elif self.direction == 'up':
                new_head = [head[0], head[1] - self.SPACE_SIZE]
            else:
                new_head = [head[0], head[1] + self.SPACE_SIZE]
            if (new_head[0] < 0 or new_head[0] >= self.GAME_WIDTH or
                new_head[1] < 0 or new_head[1] >= self.GAME_HEIGHT or
                new_head in self.snake_positions[1:]):
                self.game_over()
                return
            self.snake_positions.insert(0, new_head)
            # Draw new head (oval)
            head_oval = self.canvas.create_oval(
                new_head[0], new_head[1],
                new_head[0] + self.SPACE_SIZE, new_head[1] + self.SPACE_SIZE,
                fill=self.SNAKE_COLOR,
                outline=self.SNAKE_OUTLINE,
                width=2,
                tags="snake"
            )
            self.snake_body.insert(0, head_oval)
            # Draw eyes on head
            eye_radius = self.SPACE_SIZE // 7
            eye_offset_x = self.SPACE_SIZE // 4
            eye_offset_y = self.SPACE_SIZE // 4
            self.canvas.create_oval(
                new_head[0] + eye_offset_x, new_head[1] + eye_offset_y,
                new_head[0] + eye_offset_x + eye_radius, new_head[1] + eye_offset_y + eye_radius,
                fill="#ffffff",
                outline="",
                tags="snake_eye"
            )
            self.canvas.create_oval(
                new_head[0] + self.SPACE_SIZE - eye_offset_x - eye_radius, new_head[1] + eye_offset_y,
                new_head[0] + self.SPACE_SIZE - eye_offset_x, new_head[1] + eye_offset_y + eye_radius,
                fill="#ffffff",
                outline="",
                tags="snake_eye"
            )
            # Draw tongue (red line)
            tongue_x1 = new_head[0] + self.SPACE_SIZE // 2
            tongue_y1 = new_head[1] + self.SPACE_SIZE
            tongue_x2 = tongue_x1
            tongue_y2 = tongue_y1 + self.SPACE_SIZE // 2
            self.canvas.create_line(
                tongue_x1, tongue_y1, tongue_x2, tongue_y2,
                fill="#ff0000",
                width=2,
                tags="snake_tongue"
            )
            if new_head == self.food_position:
                self.score += 1
                self.food_count += 1
                self.score_label.config(text=f"Score: {self.score}")
                self.food_position = []
                self.canvas.delete("food")
                if self.food_count % 5 == 0:
                    self.spawn_bonus_food()
            else:
                if self.snake_body:
                    self.canvas.delete(self.snake_body.pop())
                if self.snake_positions:
                    self.snake_positions.pop()
            # Draw yellow spot on new body segment (not head)
            if len(self.snake_positions) > 1:
                body_pos = self.snake_positions[1]
                spot_size = self.SPACE_SIZE // 2
                spot_offset = self.SPACE_SIZE // 4
                self.canvas.create_oval(
                    body_pos[0] + spot_offset, body_pos[1] + spot_offset,
                    body_pos[0] + spot_offset + spot_size, body_pos[1] + spot_offset + spot_size,
                    fill=self.SNAKE_SPOT,
                    outline="",
                    tags="snake_spot"
                )
            # Remove old eyes, tongue, and spots from tail
            self.canvas.delete("snake_eye")
            self.canvas.delete("snake_tongue")
            self.canvas.delete("snake_spot")
            # Redraw all body spots except head
            for i in range(1, len(self.snake_positions)):
                pos = self.snake_positions[i]
                spot_size = self.SPACE_SIZE // 2
                spot_offset = self.SPACE_SIZE // 4
                self.canvas.create_oval(
                    pos[0] + spot_offset, pos[1] + spot_offset,
                    pos[0] + spot_offset + spot_size, pos[1] + spot_offset + spot_size,
                    fill=self.SNAKE_SPOT,
                    outline="",
                    tags="snake_spot"
                )
            if new_head == self.bonus_food_position:
                self.score += 20
                self.score_label.config(text=f"Score: {self.score}")
                self.remove_bonus_food()
            if not self.food_position:
                self.spawn_food()
            if self.game_active:
                self.movement_timer = self.root.after(self.speed, self.move_snake)
        except Exception as e:
            messagebox.showerror("Error", f"Error in game loop: {str(e)}")
            self.game_over()

    def spawn_food(self):
        try:
            max_attempts = 100
            attempts = 0
            while attempts < max_attempts:
                x = random.randint(0, (self.GAME_WIDTH - self.SPACE_SIZE) // self.SPACE_SIZE) * self.SPACE_SIZE
                y = random.randint(0, (self.GAME_HEIGHT - self.SPACE_SIZE) // self.SPACE_SIZE) * self.SPACE_SIZE
                position = [x, y]
                if position not in self.snake_positions and position != self.bonus_food_position:
                    self.food_position = position
                    self.canvas.create_oval(
                        x, y, x+self.SPACE_SIZE, y+self.SPACE_SIZE,
                        fill=self.FOOD_COLOR,
                        outline="",
                        tags="food"
                    )
                    return
                attempts += 1
            corners = [
                [0, 0],
                [self.GAME_WIDTH - self.SPACE_SIZE, 0],
                [0, self.GAME_HEIGHT - self.SPACE_SIZE],
                [self.GAME_WIDTH - self.SPACE_SIZE, self.GAME_HEIGHT - self.SPACE_SIZE]
            ]
            for corner in corners:
                if corner not in self.snake_positions and corner != self.bonus_food_position:
                    self.food_position = corner
                    self.canvas.create_oval(
                        corner[0], corner[1], corner[0]+self.SPACE_SIZE, corner[1]+self.SPACE_SIZE,
                        fill=self.FOOD_COLOR,
                        outline="",
                        tags="food"
                    )
                    return
            self.game_over()
        except Exception as e:
            messagebox.showerror("Error", f"Error spawning food: {str(e)}")
            self.game_over()

    def spawn_bonus_food(self):
        try:
            if not self.game_active:
                return
            self.remove_bonus_food()
            max_attempts = 100
            attempts = 0
            while attempts < max_attempts:
                x = random.randint(0, (self.GAME_WIDTH - self.SPACE_SIZE) // self.SPACE_SIZE) * self.SPACE_SIZE
                y = random.randint(0, (self.GAME_HEIGHT - self.SPACE_SIZE) // self.SPACE_SIZE) * self.SPACE_SIZE
                position = [x, y]
                if position not in self.snake_positions and position != self.food_position:
                    self.bonus_food_position = position
                    self.canvas.create_oval(
                        x, y, x+self.SPACE_SIZE, y+self.SPACE_SIZE,
                        fill=self.BONUS_FOOD_COLOR,
                        outline="",
                        tags="bonus_food"
                    )
                    break
                attempts += 1
            # Show and start bonus timer
            self.bonus_timer_value = 7
            self.show_bonus_timer()
            if self.bonus_food_timer:
                self.root.after_cancel(self.bonus_food_timer)
            self.bonus_food_timer = self.root.after(7000, self.remove_bonus_food)
        except Exception as e:
            messagebox.showerror("Error", f"Error spawning bonus food: {str(e)}")
            self.remove_bonus_food()

    def show_bonus_timer(self):
        # Display or update the bonus timer text on the canvas
        if hasattr(self, 'bonus_timer_text') and self.bonus_timer_text:
            self.canvas.delete(self.bonus_timer_text)
        if self.bonus_food_position:
            x, y = self.bonus_food_position
            self.bonus_timer_text = self.canvas.create_text(
                x + self.SPACE_SIZE // 2,
                y - 15,
                text=f"{self.bonus_timer_value}",
                font=('Arial', 14, 'bold'),
                fill='#ffd700',
                tags="bonus_timer"
            )
            if self.bonus_timer_value > 0:
                self.bonus_timer_value -= 1
                self.bonus_timer_update = self.root.after(1000, self.show_bonus_timer)
            else:
                self.bonus_timer_text = None
        else:
            self.bonus_timer_text = None

    def remove_bonus_food(self):
        try:
            self.canvas.delete("bonus_food")
            self.canvas.delete("bonus_timer")
            self.bonus_food_position = []
            if self.bonus_food_timer:
                self.root.after_cancel(self.bonus_food_timer)
                self.bonus_food_timer = None
            if hasattr(self, 'bonus_timer_update') and self.bonus_timer_update:
                self.root.after_cancel(self.bonus_timer_update)
                self.bonus_timer_update = None
            if hasattr(self, 'bonus_timer_text') and self.bonus_timer_text:
                self.canvas.delete(self.bonus_timer_text)
                self.bonus_timer_text = None
        except Exception as e:
            messagebox.showerror("Error", f"Error removing bonus food: {str(e)}")

    def game_over(self):
        try:
            self.game_active = False
            if self.movement_timer:
                self.root.after_cancel(self.movement_timer)
                self.movement_timer = None
            if self.bonus_food_timer:
                self.root.after_cancel(self.bonus_food_timer)
                self.bonus_food_timer = None
            self.canvas.create_text(
                self.GAME_WIDTH/2,
                self.GAME_HEIGHT/2 - 50,
                text="Game Over!",
                font=('Arial', 24),
                fill=self.TEXT_COLOR
            )
            self.canvas.create_text(
                self.GAME_WIDTH/2,
                self.GAME_HEIGHT/2,
                text=f"Final Score: {self.score}",
                font=('Arial', 20),
                fill=self.TEXT_COLOR
            )
            button_frame = tk.Frame(self.canvas, bg=self.BG_COLOR)
            button_frame.place(x=self.GAME_WIDTH/2, y=self.GAME_HEIGHT/2 + 50, anchor='center')
            yes_btn = tk.Button(
                button_frame,
                text="Yes",
                font=('Arial', 12),
                command=self.show_start_screen
            )
            yes_btn.pack(side=tk.LEFT, padx=10)
            no_btn = tk.Button(
                button_frame,
                text="No",
                font=('Arial', 12),
                command=self.root.quit
            )
            no_btn.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            messagebox.showerror("Error", f"Error in game over: {str(e)}")
            self.root.quit()

    def change_direction(self, new_direction):
        if not self.game_active:
            return
        
        # Prevent 180-degree turns
        if (new_direction == 'right' and self.direction != 'left') or \
           (new_direction == 'left' and self.direction != 'right') or \
           (new_direction == 'up' and self.direction != 'down') or \
           (new_direction == 'down' and self.direction != 'up'):
            self.direction = new_direction

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
