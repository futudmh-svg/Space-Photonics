"""
Real-time Data Streaming Interface

Streams simulation data for live monitoring and dashboards.
"""

import json
import time
from typing import Callable, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class StreamingConfig:
    """Data streaming configuration."""
    buffer_size: int = 1000         # Number of samples to buffer
    stream_rate: float = 10.0       # Stream rate [Hz]
    enable_jsonl: bool = True       # Output JSON Lines format
    enable_websocket: bool = False  # WebSocket output (requires optional deps)


class DataStreamer:
    """
    Real-time data streaming from digital twin.
    
    Supports:
    - In-memory circular buffer
    - JSON Lines file output
    - Callback-based streaming
    """
    
    def __init__(self, config: StreamingConfig):
        self.cfg = config
        self.buffer = deque(maxlen=config.buffer_size)
        self.callbacks: list[Callable] = []
        self.running = False
        self.sample_count = 0
        
        # File output
        self._file_handle = None
        
    def register_callback(self, callback: Callable):
        """Register callback for streaming data."""
        self.callbacks.append(callback)
        
    def start_file_output(self, filepath: str):
        """Start JSON Lines file output."""
        self._file_handle = open(filepath, 'w')
        print(f"Streaming to {filepath}")
        
    def stop_file_output(self):
        """Stop file output."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
            
    def push(self, data: dict):
        """
        Push data sample to stream.
        
        Args:
            data: Data dictionary to stream
        """
        # Add timestamp
        data['_stream_timestamp'] = time.time()
        data['_sample_id'] = self.sample_count
        
        # Buffer
        self.buffer.append(data)
        
        # File output
        if self._file_handle and self.cfg.enable_jsonl:
            self._file_handle.write(json.dumps(data) + '\n')
            self._file_handle.flush()
        
        # Callbacks
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
        
        self.sample_count += 1
        
    def get_recent(self, n: int = 100) -> list:
        """
        Get recent samples from buffer.
        
        Args:
            n: Number of samples
            
        Returns:
            List of recent samples
        """
        return list(self.buffer)[-n:]
    
    def get_stats(self) -> dict:
        """Get streaming statistics."""
        return {
            'total_samples': self.sample_count,
            'buffer_size': len(self.buffer),
            'buffer_capacity': self.cfg.buffer_size,
            'callbacks_registered': len(self.callbacks)
        }
    
    def clear_buffer(self):
        """Clear circular buffer."""
        self.buffer.clear()


def example_dashboard_callback(data: dict):
    """Example callback for dashboard updates."""
    if 'optical' in data:
        snr = data['optical'].get('snr_db', 0)
        print(f"\rSNR: {snr:.1f} dB | Sample: {data['_sample_id']}", end='')


if __name__ == "__main__":
    # Demo streaming
    streamer = DataStreamer(StreamingConfig())
    streamer.register_callback(example_dashboard_callback)
    streamer.start_file_output("stream_output.jsonl")
    
    # Simulate data
    import numpy as np
    for i in range(100):
        data = {
            'time': i * 0.1,
            'optical': {
                'snr_db': 20 + np.random.normal(0, 2),
                'rx_power_dbm': -50 + np.random.normal(0, 1)
            }
        }
        streamer.push(data)
        time.sleep(0.01)
    
    streamer.stop_file_output()
    print(f"\n\nStreaming stats: {streamer.get_stats()}")
