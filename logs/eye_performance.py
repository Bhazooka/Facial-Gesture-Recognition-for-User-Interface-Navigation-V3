import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import time
import json
import os
from datetime import datetime

class EyePerformanceMetrics:
    def __init__(self, history_size=100):
        # Initialize metrics storage
        self.history_size = history_size
        self.inference_times = deque(maxlen=history_size)
        self.gaze_errors = deque(maxlen=history_size)
        self.fps_history = deque(maxlen=history_size)
        self.jitter_values = deque(maxlen=history_size)
        
        # For FPS calculation
        self.frame_times = deque(maxlen=30)  # Store last 30 frame times
        self.last_frame_time = time.time()
        
        # For jitter calculation
        self.last_prediction = None
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.logs_dir, exist_ok=True)

    def update_inference_time(self, inference_time):
        """Log the time taken for a single inference"""
        self.inference_times.append(inference_time * 1000)  # Convert to milliseconds

    def update_fps(self):
        """Calculate and update FPS"""
        current_time = time.time()
        self.frame_times.append(current_time - self.last_frame_time)
        self.last_frame_time = current_time
        
        if len(self.frame_times) > 1:
            fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
            self.fps_history.append(fps)

    def update_jitter(self, current_prediction):
        """Calculate and update jitter between consecutive predictions"""
        if self.last_prediction is not None and current_prediction is not None:
            jitter = np.linalg.norm(
                np.array(current_prediction) - np.array(self.last_prediction)
            )
            self.jitter_values.append(jitter)
        self.last_prediction = current_prediction

    def save_metrics(self):
        """Save metrics to a JSON file"""
        metrics_data = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'inference_times': list(self.inference_times),
            'fps_history': list(self.fps_history),
            'jitter_values': list(self.jitter_values),
            'summary': {
                'avg_inference_time': float(np.mean(self.inference_times)) if self.inference_times else 0,
                'avg_fps': float(np.mean(self.fps_history)) if self.fps_history else 0,
                'avg_jitter': float(np.mean(self.jitter_values)) if self.jitter_values else 0,
                'std_inference_time': float(np.std(self.inference_times)) if self.inference_times else 0,
                'std_fps': float(np.std(self.fps_history)) if self.fps_history else 0,
                'std_jitter': float(np.std(self.jitter_values)) if self.jitter_values else 0
            }
        }
        
        filename = os.path.join(self.logs_dir, f'performance_{metrics_data["timestamp"]}.json')
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=4)
        return filename

    def plot_metrics(self):
        """Plot all metrics when system terminates"""
        if not (self.inference_times or self.fps_history or self.jitter_values):
            print("No performance data available to plot.")
            return

        # Save metrics before plotting
        self.save_metrics()

        plt.style.use('seaborn')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Eye Tracking Performance Metrics', fontsize=16)

        # Plot 1: Inference Time
        if self.inference_times:
            ax1.plot(list(self.inference_times), 'b-', label='Inference Time')
            ax1.set_title('Inference Time per Frame')
            ax1.set_xlabel('Frame')
            ax1.set_ylabel('Time (ms)')
            ax1.grid(True)

        # Plot 2: FPS
        if self.fps_history:
            ax2.plot(list(self.fps_history), 'g-', label='FPS')
            ax2.set_title('Frames Per Second (FPS)')
            ax2.set_xlabel('Frame')
            ax2.set_ylabel('FPS')
            ax2.grid(True)

        # Plot 3: Jitter
        if self.jitter_values:
            ax3.plot(list(self.jitter_values), 'r-', label='Jitter')
            ax3.set_title('Gaze Prediction Jitter')
            ax3.set_xlabel('Frame')
            ax3.set_ylabel('Pixels')
            ax3.grid(True)

        # Plot 4: Summary Statistics
        stats_text = (
            f'Average Metrics:\n'
            f'Inference Time: {np.mean(self.inference_times):.2f} ms\n'
            f'FPS: {np.mean(self.fps_history):.2f}\n'
            f'Jitter: {np.mean(self.jitter_values):.2f} pixels\n\n'
            f'Standard Deviations:\n'
            f'Inference Time: {np.std(self.inference_times):.2f} ms\n'
            f'FPS: {np.std(self.fps_history):.2f}\n'
            f'Jitter: {np.std(self.jitter_values):.2f} pixels'
        )
        ax4.text(0.1, 0.5, stats_text, fontsize=10, va='center')
        ax4.set_title('Summary Statistics')
        ax4.axis('off')

        plt.tight_layout()
        plt.show()
