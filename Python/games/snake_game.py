
import tkinter as tk
import random
import os

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("This is Snake Game")
        self.root.resizable(False, False)

        self.cell_size = 20
        self.width_cells = 30
        self.height_cells = 20
        self.width = self.width_cells * self.cell_size
        self.height = self.height_cells * self.cell_size

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="White")
        self.canvas.pack()

        # Score setup
        self.score = 0
        self.high_score = self.load_high_score()
        self.score_label = tk.Label(root, text=f"Score: 0  High Score: {self.high_score}", 
                                  font=("Arial", 12), bg="white")
        self.score_label.pack(fill=tk.X)

        self.direction = "Right"
        self.next_direction = "Right"
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = None
        self.running = False
        self.game_over = False

        self.root.bind("<Key>", self.handle_keypress)
        
        self.create_start_screen()

    def load_high_score(self):
        try:
            if os.path.exists("high_score.txt"):
                with open("high_score.txt", "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))

    def create_start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.width/2, self.height/3, text="SNAKE", 
                              fill="#00ff00", font=("Courier", 40, "bold"))
        self.canvas.create_text(self.width/2, self.height/2, text="Press Space to Start", 
                              fill="white", font=("Arial", 16))
        
    def start_game(self):
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.update_score()
        self.running = True
        self.game_over = False
        self.spawn_food()
        self.game_loop()

    def spawn_food(self):
        while True:
            x = random.randint(0, self.width_cells - 1)
            y = random.randint(0, self.height_cells - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def handle_keypress(self, event):
        key = event.keysym
        if not self.running and not self.game_over and key == "space":
            self.start_game()
        elif self.game_over and key == "space":
            self.create_start_screen()
            self.game_over = False
        elif self.running:
            if key == "Up" and self.direction != "Down":
                self.next_direction = "Up"
            elif key == "Down" and self.direction != "Up":
                self.next_direction = "Down"
            elif key == "Left" and self.direction != "Right":
                self.next_direction = "Left"
            elif key == "Right" and self.direction != "Left":
                self.next_direction = "Right"

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}  High Score: {self.high_score}")

    def game_loop(self):
        if not self.running:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]

        if self.direction == "Up": head_y -= 1
        elif self.direction == "Down": head_y += 1
        elif self.direction == "Left": head_x -= 1
        elif self.direction == "Right": head_x += 1

        # Check collisions
        if (head_x < 0 or head_x >= self.width_cells or 
            head_y < 0 or head_y >= self.height_cells or 
            (head_x, head_y) in self.snake):
            self.end_game()
            return

        new_head = (head_x, head_y)
        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.update_score()
            self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        self.root.after(200, self.game_loop)

    def draw(self):
        self.canvas.delete("all")
        
        # Draw Food
        if self.food:
            x, y = self.food
            self.canvas.create_oval(x*self.cell_size, y*self.cell_size, 
                                  (x+1)*self.cell_size, (y+1)*self.cell_size, 
                                  fill="red", outline="red")

        # Draw Snake
        for x, y in self.snake:
            self.canvas.create_rectangle(x*self.cell_size, y*self.cell_size, 
                                       (x+1)*self.cell_size, (y+1)*self.cell_size, 
                                       fill="#00ff00", outline="black")

    def end_game(self):
        self.running = False
        self.game_over = True
        self.save_high_score()
        self.update_score()
        self.canvas.create_text(self.width/2, self.height/2, text="GAME OVER", 
                              fill="Yellow", font=("Courier", 30, "bold"))
        self.canvas.create_text(self.width/2, self.height/2 + 40, text="Press Space to Menu", 
                              fill="Blue", font=("Arial", 14))

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
