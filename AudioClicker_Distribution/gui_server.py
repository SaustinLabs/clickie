"""
GUI Server for Remote Audio Clicker
Provides a clean interface instead of command line
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import webbrowser
import sys
import os

# Import the Flask app
from app import app, clicker, public_tunnel_url, NGROK_AVAILABLE, NGROK_AUTH_TOKEN, setup_tunnel

class AudioClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Remote Audio Clicker Server")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Configure colors
        self.bg_color = "#2b2d42"
        self.accent_color = "#8d99ae"
        self.success_color = "#06ffa5"
        self.info_color = "#00b4d8"
        
        self.root.configure(bg=self.bg_color)
        
        self.server_running = False
        self.server_thread = None
        self.tunnel_url = None
        
        self.setup_ui()
        self.update_stats()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(pady=20)
        
        title = tk.Label(header, text="🎮 Remote Audio Clicker", 
                        font=("Arial", 24, "bold"),
                        bg=self.bg_color, fg=self.success_color)
        title.pack()
        
        subtitle = tk.Label(header, text="Server Control Panel", 
                           font=("Arial", 12),
                           bg=self.bg_color, fg=self.accent_color)
        subtitle.pack()
        
        # Status Section
        status_frame = tk.LabelFrame(self.root, text="🔌 Server Status", 
                                     font=("Arial", 12, "bold"),
                                     bg=self.bg_color, fg=self.accent_color,
                                     relief=tk.GROOVE, borderwidth=2)
        status_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="⭕ Stopped", 
                                     font=("Arial", 14, "bold"),
                                     bg=self.bg_color, fg="#ef233c")
        self.status_label.pack(pady=10)
        
        # Control Buttons
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.start_btn = tk.Button(button_frame, text="▶️ Start Server",
                                   command=self.start_server,
                                   font=("Arial", 12, "bold"),
                                   bg="#06ffa5", fg="#000000",
                                   width=15, height=2,
                                   relief=tk.RAISED, borderwidth=3,
                                   cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="⏹️ Stop Server",
                                  command=self.stop_server,
                                  font=("Arial", 12, "bold"),
                                  bg="#ef233c", fg="#ffffff",
                                  width=15, height=2,
                                  relief=tk.RAISED, borderwidth=3,
                                  cursor="hand2", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # URL Section
        url_frame = tk.LabelFrame(self.root, text="🌍 Public Access URL", 
                                 font=("Arial", 12, "bold"),
                                 bg=self.bg_color, fg=self.accent_color,
                                 relief=tk.GROOVE, borderwidth=2)
        url_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.url_text = tk.Text(url_frame, height=2, font=("Courier", 10),
                               bg="#1a1d2e", fg=self.success_color,
                               relief=tk.SUNKEN, borderwidth=2,
                               wrap=tk.WORD)
        self.url_text.pack(pady=5, padx=10, fill=tk.X)
        self.url_text.insert("1.0", "🔒 Server not started yet...")
        self.url_text.config(state=tk.DISABLED)
        
        url_btn_frame = tk.Frame(url_frame, bg=self.bg_color)
        url_btn_frame.pack(pady=5)
        
        self.copy_btn = tk.Button(url_btn_frame, text="📋 Copy URL",
                                 command=self.copy_url,
                                 font=("Arial", 10),
                                 bg=self.info_color, fg="#ffffff",
                                 cursor="hand2", state=tk.DISABLED)
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = tk.Button(url_btn_frame, text="🌐 Open in Browser",
                                 command=self.open_browser,
                                 font=("Arial", 10),
                                 bg=self.info_color, fg="#ffffff",
                                 cursor="hand2", state=tk.DISABLED)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Stats Section
        stats_frame = tk.LabelFrame(self.root, text="📊 Statistics", 
                                   font=("Arial", 12, "bold"),
                                   bg=self.bg_color, fg=self.accent_color,
                                   relief=tk.GROOVE, borderwidth=2)
        stats_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        stats_grid = tk.Frame(stats_frame, bg=self.bg_color)
        stats_grid.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Total Clicks
        tk.Label(stats_grid, text="Total Clicks:", font=("Arial", 11),
                bg=self.bg_color, fg=self.accent_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.total_clicks_label = tk.Label(stats_grid, text="0", font=("Arial", 11, "bold"),
                                          bg=self.bg_color, fg=self.success_color)
        self.total_clicks_label.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Today's Clicks
        tk.Label(stats_grid, text="Today's Clicks:", font=("Arial", 11),
                bg=self.bg_color, fg=self.accent_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.daily_clicks_label = tk.Label(stats_grid, text="0", font=("Arial", 11, "bold"),
                                          bg=self.bg_color, fg=self.success_color)
        self.daily_clicks_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # Local URL
        tk.Label(stats_grid, text="Local URL:", font=("Arial", 11),
                bg=self.bg_color, fg=self.accent_color).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.local_url_label = tk.Label(stats_grid, text="http://localhost:5000", 
                                        font=("Arial", 10),
                                        bg=self.bg_color, fg=self.info_color,
                                        cursor="hand2")
        self.local_url_label.grid(row=2, column=1, sticky=tk.W, pady=5, padx=10)
        self.local_url_label.bind("<Button-1>", lambda e: webbrowser.open("http://localhost:5000"))
        
        # Activity Log
        log_frame = tk.LabelFrame(self.root, text="📝 Recent Activity", 
                                 font=("Arial", 10, "bold"),
                                 bg=self.bg_color, fg=self.accent_color,
                                 relief=tk.GROOVE, borderwidth=2)
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, font=("Courier", 9),
                               bg="#1a1d2e", fg=self.accent_color,
                               relief=tk.SUNKEN, borderwidth=2,
                               wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # Footer
        footer = tk.Label(self.root, text="Made with 💜 for long distance relationships", 
                         font=("Arial", 9, "italic"),
                         bg=self.bg_color, fg=self.accent_color)
        footer.pack(pady=10)
        
        self.log("✨ GUI initialized - ready to start!")
        
    def log(self, message):
        """Add message to activity log"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def start_server(self):
        """Start Flask server in background thread"""
        if self.server_running:
            return
            
        self.log("🚀 Starting Flask server...")
        self.server_running = True
        
        # Update UI
        self.status_label.config(text="✅ Running", fg=self.success_color)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start Flask in thread
        self.server_thread = threading.Thread(target=self.run_flask, daemon=True)
        self.server_thread.start()
        
        # Setup ngrok after delay
        if NGROK_AVAILABLE and NGROK_AUTH_TOKEN.strip():
            self.log("🌐 Setting up ngrok tunnel...")
            threading.Thread(target=self.setup_ngrok_delayed, daemon=True).start()
        else:
            self.log("⚠️ Ngrok not configured - local access only")
            
    def run_flask(self):
        """Run Flask app (in background thread)"""
        try:
            self.log("📡 Server listening on http://localhost:5000")
            app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        except Exception as e:
            self.log(f"❌ Server error: {e}")
            self.server_running = False
            
    def setup_ngrok_delayed(self):
        """Setup ngrok tunnel after server starts"""
        time.sleep(3)  # Wait for Flask to start
        
        try:
            success = setup_tunnel()
            if success:
                global public_tunnel_url
                from app import public_tunnel_url
                self.tunnel_url = public_tunnel_url
                
                # Update UI on main thread
                self.root.after(0, self.update_tunnel_url)
                self.log(f"✅ Tunnel ready: {public_tunnel_url}")
            else:
                self.log("❌ Tunnel setup failed - check your auth token")
        except Exception as e:
            self.log(f"❌ Tunnel error: {e}")
            
    def update_tunnel_url(self):
        """Update URL display (must be called on main thread)"""
        if self.tunnel_url:
            self.url_text.config(state=tk.NORMAL)
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert("1.0", f"🌍 {self.tunnel_url}\n\n💡 Share this with friends!")
            self.url_text.config(state=tk.DISABLED)
            
            self.copy_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.NORMAL)
        else:
            self.url_text.config(state=tk.NORMAL)
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert("1.0", "🔒 Local only: http://localhost:5000")
            self.url_text.config(state=tk.DISABLED)
            
    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            return
            
        self.log("🛑 Stopping server...")
        self.server_running = False
        
        # Update UI
        self.status_label.config(text="⭕ Stopped", fg="#ef233c")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.copy_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        
        # Note: Flask doesn't have clean shutdown in thread, so we just exit
        self.log("⚠️ Please close and restart to start server again")
        
    def copy_url(self):
        """Copy tunnel URL to clipboard"""
        if self.tunnel_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.tunnel_url)
            self.log("📋 URL copied to clipboard!")
            messagebox.showinfo("Copied!", "URL copied to clipboard!")
        else:
            self.root.clipboard_clear()
            self.root.clipboard_append("http://localhost:5000")
            self.log("📋 Local URL copied to clipboard!")
            
    def open_browser(self):
        """Open URL in default browser"""
        url = self.tunnel_url if self.tunnel_url else "http://localhost:5000"
        self.log(f"🌐 Opening {url} in browser...")
        webbrowser.open(url)
        
    def update_stats(self):
        """Update statistics display"""
        if self.server_running:
            # Update click counts
            self.total_clicks_label.config(text=str(clicker.click_count))
            self.daily_clicks_label.config(text=str(clicker.daily_click_count))
            
        # Schedule next update
        self.root.after(1000, self.update_stats)
        
    def on_closing(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Stop server and quit?"):
            self.log("👋 Shutting down...")
            self.server_running = False
            self.root.destroy()
            os._exit(0)  # Force exit

def main():
    root = tk.Tk()
    gui = AudioClickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
