"""
OCR Desktop Application - Handwritten Digit Recognition
Uses a custom k-Nearest Neighbors classifier (no pre-built OCR libraries).
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
            # Compute Euclidean distances to all training samples
            distances = np.sqrt(np.sum((self.X_train - sample) ** 2, axis=1))
            
            # Get indices of k nearest neighbors
            k_indices = np.argsort(distances)[:self.k]
            
            # Get labels of k nearest neighbors
            k_labels = self.y_train[k_indices]
            
            # Return most common label (majority vote)
            unique, counts = np.unique(k_labels, return_counts=True)
            predictions.append(unique[np.argmax(counts)])
        
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Return confidence scores for predictions."""
        X = np.array(X).astype(np.float32)
        results = []
        
        for sample in X:
            distances = np.sqrt(np.sum((self.X_train - sample) ** 2, axis=1))
            k_indices = np.argsort(distances)[:self.k]
            k_distances = distances[k_indices]
            k_labels = self.y_train[k_indices]
            
            # Weight by inverse distance
            weights = 1 / (k_distances + 1e-6)
            
            # Count weighted votes for each class
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

# --- Data Loading ---
def load_mnist_data(sample_size=10000):
    """Load MNIST data. Uses sklearn only for data fetching, not classification."""
    cache_file = "mnist_cache.pkl"
    
    if os.path.exists(cache_file):
        print("Loading MNIST from cache...")
        with open(cache_file, 'rb') as f:
            X, y = pickle.load(f)
        print(f"Loaded {len(X)} training samples from cache")
        return X, y
    
    print("Downloading MNIST dataset (first run only)...")
    from sklearn.datasets import fetch_openml
    
    mnist = fetch_openml('mnist_784', version=1, as_frame=False, parser='liac-arff')
    X, y = mnist.data, mnist.target.astype(int)
    
    # Subsample for faster prediction (full dataset is 70K samples)
    indices = np.random.choice(len(X), sample_size, replace=False)
    X = X[indices]
    y = y[indices]
    
    # Normalize
    X = X / 255.0
    
    # Cache for future runs
    with open(cache_file, 'wb') as f:
        pickle.dump((X, y), f)
    
    print(f"Loaded {len(X)} training samples")
    return X, y

# --- Image Preprocessing ---
def preprocess_image(pil_image):
    """Convert drawn image to MNIST-compatible format."""
    # Convert to grayscale
    img = pil_image.convert('L')
    
    # Invert (MNIST: white digit on black background)
    img = ImageOps.invert(img)
    
    # Find bounding box of the digit
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
    
    # Resize to 28x28 (MNIST standard)
    img = new_img.resize((28, 28), Image.Resampling.LANCZOS)
    
    # Convert to numpy array and normalize
    arr = np.array(img).astype(np.float32) / 255.0
    
    return arr.flatten()

# --- GUI Application ---
class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Handwritten Digit Recognition (Custom OCR)")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize classifier
        self.classifier = None
        self.loading = True
        
        # Drawing state
        self.last_x = None
        self.last_y = None
        
        # Create PIL image for drawing
        self.canvas_size = 280
        self.image = Image.new('RGB', (self.canvas_size, self.canvas_size), 'white')
        self.draw = ImageDraw.Draw(self.image)
        
        self.setup_ui()
        self.load_model()
    
    def setup_ui(self):
        # Main container - use tk.Frame not ttk.Frame to avoid style conflicts
        main_frame = tk.Frame(self.root, bg='#1e1e1e', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="Draw a Digit (0-9)", 
                        font=('Segoe UI', 18, 'bold'),
                        bg='#1e1e1e', fg='white')
        title.pack(pady=(0, 15))
        
        # Canvas for drawing
        self.canvas = tk.Canvas(main_frame, 
                               width=self.canvas_size, 
                               height=self.canvas_size,
                               bg='white', 
                               cursor='cross',
                               highlightthickness=2,
                               highlightbackground='#3b82f6')
        self.canvas.pack(pady=10)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw_line)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        # Style for buttons
        style = ttk.Style()
        style.configure('Primary.TButton', font=('Segoe UI', 12))
        
        self.recognize_btn = ttk.Button(btn_frame, text="🔍 Recognize", 
                                        command=self.recognize, style='Primary.TButton')
        self.recognize_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="🗑️ Clear", 
                                   command=self.clear_canvas, style='Primary.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Result display - use Text widget instead of Label (more reliable rendering)
        self.result_text_widget = tk.Text(main_frame, height=2, width=30,
                                          font=('Segoe UI', 18, 'bold'),
                                          bg='#333333', fg='#00ff00',
                                          relief=tk.FLAT, wrap=tk.WORD,
                                          state=tk.DISABLED)
        self.result_text_widget.pack(fill=tk.X, pady=10)
        self._update_result("Draw a digit and click Recognize", "#ffffff")
        
        # Confidence display
        self.confidence_widget = tk.Text(main_frame, height=1, width=30,
                                        font=('Segoe UI', 12),
                                        bg='#333333', fg='#00ffff',
                                        relief=tk.FLAT,
                                        state=tk.DISABLED)
        self.confidence_widget.pack(fill=tk.X)
        
        # Status bar
        self.status_label = tk.Label(main_frame, 
                                    text="Loading MNIST data...",
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
        """Load MNIST data and train classifier in background."""
        def do_load():
            X, y = load_mnist_data(sample_size=10000)
            self.classifier = KNNClassifier(k=5)
            self.classifier.fit(X, y)
            self.loading = False
            print("Model ready!")
            # Schedule UI update on main thread (thread-safe)
            self.root.after(0, lambda: self.status_label.config(text="Ready! Draw a digit and click Recognize."))
        
        import threading
        threading.Thread(target=do_load, daemon=True).start()
    
    def start_draw(self, event):
        self.last_x = event.x
        self.last_y = event.y
    
    def draw_line(self, event):
        if self.last_x and self.last_y:
            # Draw on canvas
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                   fill='black', width=18, capstyle=tk.ROUND)
            # Draw on PIL image
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
        self._update_result("Draw a digit and click Recognize", "#ffffff")
        self._update_confidence("")
    
    def recognize(self):
        print("=== Recognize button clicked ===")
        print(f"Loading state: {self.loading}")
        print(f"Classifier: {self.classifier}")
        
        if self.loading:
            print("Still loading, returning early")
            self.result_label.config(text="Still loading model...", fg='orange')
            return
        
        try:
            print("Preprocessing image...")
            # Preprocess the drawn image
            processed = preprocess_image(self.image)
            print(f"Processed shape: {processed.shape}, max: {np.max(processed)}")
            
            # Check if canvas is empty
            if np.max(processed) < 0.1:
                print("Canvas appears empty")
                self.result_label.config(text="Please draw something first!", fg='orange')
                return
            
            print("Running prediction...")
            # Predict
            prediction = self.classifier.predict([processed])[0]
            print(f"Prediction: {prediction}")
            proba = self.classifier.predict_proba([processed])[0]
            print(f"Proba: {proba}")
            
            confidence = proba.get(int(prediction), 0) * 100
            print(f"Confidence: {confidence}")
            
            # Update UI using Text widgets
            print("Updating UI...")
            self._update_result(f"Predicted: {prediction}", "#00ff00")
            self._update_confidence(f"Confidence: {confidence:.1f}%")
            # Force UI refresh
            self.root.update_idletasks()
            print("Done!")
        except Exception as e:
            print(f"Recognition error: {e}")
            import traceback
            traceback.print_exc()
            self._update_result(f"Error: {e}", "#ff0000")

def main():
    root = tk.Tk()
    root.geometry("360x520")
    root.resizable(False, False)
    
    # Dark theme
    root.configure(bg='#1e1e1e')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('.', background='#1e1e1e', foreground='white')
    style.configure('TFrame', background='#1e1e1e')
    style.configure('TButton', padding=10, font=('Segoe UI', 11))
    
    app = OCRApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
