"""
Alphabet OCR Desktop Application - Handwritten Letter Recognition (A-Z)
Uses a custom k-Nearest Neighbors classifier trained on EMNIST Letters.
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import os
import pickle

# --- Custom k-NN Classifier ---
class KNNClassifier:
    """Simple k-Nearest Neighbors classifier using Euclidean distance."""
    
    def __init__(self, k=5):
        self.k = k
        self.X_train = None
        self.y_train = None
    
    def fit(self, X, y):
        """Store training data."""
        self.X_train = np.array(X).astype(np.float32)
        self.y_train = np.array(y)
    
    def predict(self, X):
        """Predict labels for input samples."""
        X = np.array(X).astype(np.float32)
        predictions = []
        
        for sample in X:
            # Compute Euclidean distances
            # Optim: Use partial sort if set matches are huge, but simple sort ok for 10k
            diff = self.X_train - sample
            dist_sq = np.sum(diff**2, axis=1) # Squared Euclidean is enough for ranking
            
            # Get indices of k nearest neighbors
            k_indices = np.argpartition(dist_sq, self.k)[:self.k]
            
            # Get labels of k nearest neighbors
            k_labels = self.y_train[k_indices]
            
            # Vote
            unique, counts = np.unique(k_labels, return_counts=True)
            predictions.append(unique[np.argmax(counts)])
        
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Return confidence scores."""
        X = np.array(X).astype(np.float32)
        results = []
        
        for sample in X:
            diff = self.X_train - sample
            dist_sq = np.sum(diff**2, axis=1)
            distances = np.sqrt(dist_sq)
            
            k_indices = np.argsort(distances)[:self.k]
            k_distances = distances[k_indices]
            k_labels = self.y_train[k_indices]
            
            # Weight by inverse distance
            weights = 1 / (k_distances + 1e-6)
            
            # Count weighted votes
            class_scores = {}
            for label, weight in zip(k_labels, weights):
                label = int(label)
                class_scores[label] = class_scores.get(label, 0) + weight
            
            # Normalize
            total = sum(class_scores.values())
            for k in class_scores:
                class_scores[k] /= total
            
            results.append(class_scores)
        
        return results

# --- Data Loading (EMNIST) ---
def load_emnist_data(sample_size=15000):
    """Load EMNIST Letters data."""
    cache_file = "emnist_letters_cache.pkl"
    
    if os.path.exists(cache_file):
        print("Loading EMNIST from cache...")
        with open(cache_file, 'rb') as f:
            X, y = pickle.load(f)
        print(f"Loaded {len(X)} training samples from cache")
        return X, y
    
    print("Downloading EMNIST Balanced dataset (ID 41039)...")
    from sklearn.datasets import fetch_openml
    
    # EMNIST Balanced contains digits (0-9), uppercase (10-35), lowercase (36-46)
    # We will filter for Uppercase Letters (10-35)
    mnist = fetch_openml(name='EMNIST_Balanced', version=1, as_frame=False, parser='liac-arff')
    X_all, y_all = mnist.data, mnist.target.astype(int)
    
    print(f"Dataset shape: {X_all.shape}")
    
    # Filter for Uppercase Letters (Classes 10-35)
    # Class 10 = 'A', Class 35 = 'Z'
    mask = (y_all >= 10) & (y_all <= 35)
    X = X_all[mask]
    y = y_all[mask]
    
    print(f"Filtered for letters (A-Z): {len(X)} samples")
    
    # EMNIST images are rotated 90 degrees and flipped compared to standard MNIST/drawing
    # We need to fix this so they match what the user draws
    # reshape -> transpose -> flatten
    print("Fixing EMNIST orientation...")
    X_fixed = []
    for row in X:
        img = row.reshape(28, 28)
        img = np.fliplr(img)      # Flip
        img = np.rot90(img)       # Rotate to match drawing canvas orientation
        X_fixed.append(img.flatten())
    X = np.array(X_fixed)
    
    # Subsample to keep app responsive
    if len(X) > sample_size:
        indices = np.random.choice(len(X), sample_size, replace=False)
        X = X[indices]
        y = y[indices]
    
    # Normalize
    X = X / 255.0
    
    # Cache
    with open(cache_file, 'wb') as f:
        pickle.dump((X, y), f)
    
    print(f"Loaded {len(X)} training samples")
    return X, y

# --- Image Preprocessing ---
def preprocess_image(pil_image):
    """Convert drawn image to model-compatible format."""
    img = pil_image.convert('L')
    img = ImageOps.invert(img)
    
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    
    # Add padding
    padding = 20
    width, height = img.size
    max_dim = max(width, height)
    new_img = Image.new('L', (max_dim + padding * 2, max_dim + padding * 2), 0)
    
    paste_x = (max_dim + padding * 2 - width) // 2
    paste_y = (max_dim + padding * 2 - height) // 2
    new_img.paste(img, (paste_x, paste_y))
    
    img = new_img.resize((28, 28), Image.Resampling.LANCZOS)
    arr = np.array(img).astype(np.float32) / 255.0
    
    return arr.flatten()

# --- GUI Application ---
class OCRAlphabetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Handwritten Alphabet Recognition (A-Z)")
        self.root.configure(bg='#1e1e1e')
        
        self.classifier = None
        self.loading = True
        
        self.last_x = None
        self.last_y = None
        
        self.canvas_size = 280
        self.image = Image.new('RGB', (self.canvas_size, self.canvas_size), 'white')
        self.draw = ImageDraw.Draw(self.image)
        
        self.setup_ui()
        self.load_model()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#1e1e1e', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(main_frame, text="Draw a Letter (A-Z)", 
                        font=('Segoe UI', 18, 'bold'),
                        bg='#1e1e1e', fg='white')
        title.pack(pady=(0, 15))
        
        self.canvas = tk.Canvas(main_frame, 
                               width=self.canvas_size, 
                               height=self.canvas_size,
                               bg='white', 
                               cursor='cross',
                               highlightthickness=2,
                               highlightbackground='#3b82f6')
        self.canvas.pack(pady=10)
        
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw_line)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        style = ttk.Style()
        style.configure('Primary.TButton', font=('Segoe UI', 12))
        
        self.recognize_btn = ttk.Button(btn_frame, text="🔍 Recognize", 
                                        command=self.recognize, style='Primary.TButton')
        self.recognize_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear", 
                                   command=self.clear_canvas, style='Primary.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Result display
        self.result_text_widget = tk.Text(main_frame, height=2, width=30,
                                          font=('Segoe UI', 18, 'bold'),
                                          bg='#333333', fg='#00ff00',
                                          relief=tk.FLAT, wrap=tk.WORD,
                                          state=tk.DISABLED)
        self.result_text_widget.pack(fill=tk.X, pady=10)
        self._update_result("Draw a letter and click Recognize", "#ffffff")
        
        self.confidence_widget = tk.Text(main_frame, height=1, width=30,
                                        font=('Segoe UI', 12),
                                        bg='#333333', fg='#00ffff',
                                        relief=tk.FLAT,
                                        state=tk.DISABLED)
        self.confidence_widget.pack(fill=tk.X)
        
        self.status_label = tk.Label(main_frame, 
                                    text="Loading EMNIST data...",
                                    font=('Segoe UI', 10),
                                    bg='#1e1e1e', fg='#666')
        self.status_label.pack(side=tk.BOTTOM, pady=5)
    
    def _update_result(self, text, color='#00ff00'):
        """Helper to update the result Text widget."""
        self.result_text_widget.config(state=tk.NORMAL, fg=color)
        self.result_text_widget.delete('1.0', tk.END)
        self.result_text_widget.insert('1.0', text)
        self.result_text_widget.tag_configure("center", justify='center')
        self.result_text_widget.tag_add("center", "1.0", "end")
        self.result_text_widget.config(state=tk.DISABLED)
    
    def _update_confidence(self, text):
        """Helper to update the confidence Text widget."""
        self.confidence_widget.config(state=tk.NORMAL)
        self.confidence_widget.delete('1.0', tk.END)
        self.confidence_widget.insert('1.0', text)
        self.confidence_widget.tag_configure("center", justify='center')
        self.confidence_widget.tag_add("center", "1.0", "end")
        self.confidence_widget.config(state=tk.DISABLED)
    
    def load_model(self):
        def do_load():
            try:
                X, y = load_emnist_data(sample_size=15000)
                self.classifier = KNNClassifier(k=5)
                self.classifier.fit(X, y)
                self.loading = False
                print("Model ready!")
                self.root.after(0, lambda: self.status_label.config(text="Ready! Draw a letter."))
            except Exception as e:
                print(f"Error loading model: {e}")
                self.root.after(0, lambda: self.status_label.config(text="Error loading data!", fg='red'))
        
        import threading
        threading.Thread(target=do_load, daemon=True).start()
    
    def start_draw(self, event):
        self.last_x = event.x
        self.last_y = event.y
    
    def draw_line(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                   fill='black', width=18, capstyle=tk.ROUND)
            self.draw.line([self.last_x, self.last_y, event.x, event.y],
                          fill='black', width=18)
        self.last_x = event.x
        self.last_y = event.y
    
    def stop_draw(self, event):
        self.last_x = None
        self.last_y = None
    
    def clear_canvas(self):
        self.canvas.delete('all')
        self.image = Image.new('RGB', (self.canvas_size, self.canvas_size), 'white')
        self.draw = ImageDraw.Draw(self.image)
        self._update_result("Draw a letter and click Recognize", "#ffffff")
        self._update_confidence("")
    
    def recognize(self):
        if self.loading:
            self._update_result("Still loading model...", "orange")
            return
        
        try:
            processed = preprocess_image(self.image)
            
            if np.max(processed) < 0.1:
                self._update_result("Please draw something first!", "orange")
                return
            
            prediction_idx = self.classifier.predict([processed])[0]
            # Map index to Letter (10=A, 11=B, ..., 35=Z)
            # 'A' is 65 in ASCII. So 10 + 55 = 65.
            letter = chr(int(prediction_idx) + 55)
            
            proba = self.classifier.predict_proba([processed])[0]
            confidence = proba.get(int(prediction_idx), 0) * 100
            
            print(f"Pred: {prediction_idx} ({letter}), Conf: {confidence:.1f}%")
            
            # Update UI
            self._update_result(f"Predicted: {letter}", "#00ff00")
            self._update_confidence(f"Confidence: {confidence:.1f}%")
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self._update_result(f"Error: {e}", "red")

def main():
    root = tk.Tk()
    root.geometry("360x520")
    root.resizable(False, False)
    # Dark theme setup
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TButton", background="#333333", foreground="white", borderwidth=0)
    
    app = OCRAlphabetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
