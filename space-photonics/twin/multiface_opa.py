"""
Multi-Face OPA for Full-Spherical Hypersonic Vehicle Tracking

Models a VLEO satellite with 4 OPA faces:
- Face 1: +X (forward/velocity vector)
- Face 2: -X (aft)
- Face 3: +Y (starboard)
- Face 4: -Y (port)

Each face provides ~90° azimuth × 90° elevation coverage.
Together they provide near-hemispherical coverage for
tracking hypersonic vehicles during overflight.
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .opa_beamsteer import OPABeamSteerer, OPAConfig


@dataclass
class FaceConfig:
    """Configuration for a single OPA face."""
    # Face orientation in satellite body frame
    normal_azimuth: float = 0.0    # Degrees (0 = +X)
    normal_elevation: float = 0.0  # Degrees (0 = horizontal)
    
    # Coverage limits
    max_azimuth_scan: float = 45.0   # ± degrees from normal
    max_elevation_scan: float = 45.0  # ± degrees from normal
    
    # OPA parameters
    opa_config: OPAConfig = None
    
    def __post_init__(self):
        if self.opa_config is None:
            self.opa_config = OPAConfig()


@dataclass
class MultiFaceOPAConfig:
    """Configuration for multi-face OPA array."""
    # Four face configurations
    face_configs: List[FaceConfig] = None
    
    # Handoff parameters
    handoff_overlap_deg: float = 10.0  # Overlap region for smooth handoff
    handoff_threshold_db: float = 3.0   # SNR drop threshold to trigger handoff
    
    def __post_init__(self):
        if self.face_configs is None:
            # Default: 4 faces, forward, aft, starboard, port
            self.face_configs = [
                FaceConfig(normal_azimuth=0.0, normal_elevation=0.0),    # +X
                FaceConfig(normal_azimuth=180.0, normal_elevation=0.0),  # -X
                FaceConfig(normal_azimuth=90.0, normal_elevation=0.0),   # +Y
                FaceConfig(normal_azimuth=270.0, normal_elevation=0.0),  # -Y
            ]


class MultiFaceOPA:
    """
    Multi-face OPA array for full-spherical coverage.
    
    Provides:
    - Independent beam steering on each face
    - Automatic face selection for target tracking
    - Smooth handoff between faces
    - Coverage gap analysis
    """
    
    def __init__(self, config: MultiFaceOPAConfig):
        self.cfg = config
        self.num_faces = len(config.face_configs)
        
        # Create OPA for each face
        self.faces = []
        for face_cfg in config.face_configs:
            opa = OPABeamSteerer(face_cfg.opa_config)
            self.faces.append({
                'opa': opa,
                'config': face_cfg,
                'active': False,
                'current_snr': -np.inf,
            })
        
        # Tracking state
        self.target_azimuth = 0.0
        self.target_elevation = 0.0
        self.active_face_index = 0
        self.handoff_in_progress = False
        
    def compute_face_coverage(self, face_index: int) -> Tuple[float, float, float, float]:
        """
        Compute azimuth/elevation coverage limits for a face.
        
        Returns:
            (az_min, az_max, el_min, el_max) in degrees
        """
        cfg = self.faces[face_index]['config']
        az_min = cfg.normal_azimuth - cfg.max_azimuth_scan
        az_max = cfg.normal_azimuth + cfg.max_azimuth_scan
        el_min = cfg.normal_elevation - cfg.max_elevation_scan
        el_max = cfg.normal_elevation + cfg.max_elevation_scan
        return az_min, az_max, el_min, el_max
    
    def is_target_visible(self, face_index: int, azimuth: float, elevation: float) -> bool:
        """Check if target is within a face's coverage."""
        az_min, az_max, el_min, el_max = self.compute_face_coverage(face_index)
        
        # Handle azimuth wraparound
        if az_max > 360:
            return (azimuth >= az_min or azimuth <= az_max - 360) and el_min <= elevation <= el_max
        if az_min < 0:
            return (azimuth >= az_min + 360 or azimuth <= az_max) and el_min <= elevation <= el_max
        
        return az_min <= azimuth <= az_max and el_min <= elevation <= el_max
    
    def select_best_face(self, azimuth: float, elevation: float) -> int:
        """
        Select the best face for tracking a target.
        
        Returns:
            Index of best face, or -1 if no face can see target
        """
        best_face = -1
        best_score = -np.inf
        
        for i, face in enumerate(self.faces):
            if self.is_target_visible(i, azimuth, elevation):
                # Score based on angular distance from face normal
                cfg = face['config']
                az_diff = abs(azimuth - cfg.normal_azimuth)
                if az_diff > 180:
                    az_diff = 360 - az_diff
                el_diff = abs(elevation - cfg.normal_elevation)
                score = -(az_diff + el_diff)  # Closer to normal = better
                
                if score > best_score:
                    best_score = score
                    best_face = i
        
        return best_face
    
    def steer_face(self, face_index: int, azimuth: float, elevation: float):
        """
        Steer a specific face toward target.
        
        Args:
            face_index: Which face to steer
            azimuth: Target azimuth in degrees
            elevation: Target elevation in degrees
        """
        face = self.faces[face_index]
        cfg = face['config']
        
        # Compute steering angles relative to face normal
        rel_az = azimuth - cfg.normal_azimuth
        if rel_az > 180:
            rel_az -= 360
        if rel_az < -180:
            rel_az += 360
        
        rel_el = elevation - cfg.normal_elevation
        
        # Clamp to coverage limits
        rel_az = np.clip(rel_az, -cfg.max_azimuth_scan, cfg.max_azimuth_scan)
        rel_el = np.clip(rel_el, -cfg.max_elevation_scan, cfg.max_elevation_scan)
        
        face['opa'].set_steering_angle(rel_az, rel_el)
        face['active'] = True
    
    def track_target(self, azimuth: float, elevation: float):
        """
        Track a target using the best face(s).
        
        Args:
            azimuth: Target azimuth in degrees (0-360)
            elevation: Target elevation in degrees (-90 to 90)
        """
        self.target_azimuth = azimuth
        self.target_elevation = elevation
        
        # Select best face
        best_face = self.select_best_face(azimuth, elevation)
        
        if best_face < 0:
            # Target not visible by any face
            for face in self.faces:
                face['active'] = False
            return
        
        # Check if handoff needed
        if best_face != self.active_face_index and self.faces[self.active_face_index]['active']:
            # Smooth handoff: activate new face before deactivating old
            self.handoff_in_progress = True
            self.steer_face(best_face, azimuth, elevation)
            # Keep old face active briefly for overlap
            if not self.is_target_visible(self.active_face_index, azimuth, elevation):
                self.faces[self.active_face_index]['active'] = False
                self.handoff_in_progress = False
        else:
            self.steer_face(best_face, azimuth, elevation)
        
        self.active_face_index = best_face
    
    def compute_coverage_fraction(self, elevation_range=(-30, 30)) -> float:
        """
        Compute fraction of azimuth covered at given elevation range.
        
        Returns:
            Coverage fraction (0-1)
        """
        covered_azimuths = set()
        
        for az in range(0, 360, 2):
            for el in range(int(elevation_range[0]), int(elevation_range[1]) + 1, 5):
                if self.select_best_face(az, el) >= 0:
                    covered_azimuths.add(az)
                    break
        
        return len(covered_azimuths) / 360.0
    
    def get_coverage_gaps(self) -> List[Tuple[float, float]]:
        """
        Find azimuth gaps in coverage.
        
        Returns:
            List of (start_az, end_az) tuples for uncovered regions
        """
        gaps = []
        in_gap = False
        gap_start = 0
        
        for az in range(0, 360):
            visible = any(self.is_target_visible(i, az, 0) for i in range(self.num_faces))
            
            if not visible and not in_gap:
                in_gap = True
                gap_start = az
            elif visible and in_gap:
                in_gap = False
                gaps.append((gap_start, az))
        
        # Check wraparound
        if in_gap:
            gaps.append((gap_start, 360))
        
        return gaps
    
    def get_active_face_pattern(self, theta: np.ndarray) -> np.ndarray:
        """Get far-field pattern from currently active face."""
        face = self.faces[self.active_face_index]
        if face['active']:
            return face['opa'].compute_farfield(theta)
        return np.zeros_like(theta)


def demo_multiface_tracking():
    """Demonstrate multi-face OPA tracking a hypersonic vehicle."""
    import matplotlib.pyplot as plt
    
    print("=" * 70)
    print("Multi-Face OPA Demo — Hypersonic Vehicle Tracking")
    print("=" * 70)
    
    # Create multi-face OPA
    config = MultiFaceOPAConfig()
    mf_opa = MultiFaceOPA(config)
    
    # Coverage analysis
    print("\n1. Coverage Analysis")
    print("-" * 50)
    for i in range(mf_opa.num_faces):
        az_min, az_max, el_min, el_max = mf_opa.compute_face_coverage(i)
        print(f"  Face {i+1}: AZ=[{az_min:.0f}°, {az_max:.0f}°], "
              f"EL=[{el_min:.0f}°, {el_max:.0f}°]")
    
    coverage = mf_opa.compute_coverage_fraction()
    print(f"\n  Total azimuth coverage at EL=0°: {coverage*100:.1f}%")
    
    gaps = mf_opa.get_coverage_gaps()
    if gaps:
        print(f"  Coverage gaps: {len(gaps)} regions")
        for start, end in gaps:
            print(f"    {start}° - {end}°")
    else:
        print("  No gaps in coverage!")
    
    # Simulate hypersonic flyover
    print("\n2. Hypersonic Flyover Simulation")
    print("-" * 50)
    print("  Vehicle: Mach 10, passing directly overhead")
    
    # Vehicle trajectory: approaches from horizon, passes overhead, departs
    times = np.linspace(0, 20, 100)  # 20 seconds
    
    # Simple overflight: azimuth 0°, elevation goes 0→90→0
    azimuths = np.zeros_like(times)
    elevations = 90 * np.sin(np.pi * times / 20)
    
    active_faces = []
    for t, az, el in zip(times, azimuths, elevations):
        mf_opa.track_target(az, el)
        active_faces.append(mf_opa.active_face_index)
    
    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Elevation vs time
    axes[0].plot(times, elevations, 'b-', linewidth=2, label='Target Elevation')
    axes[0].set_ylabel('Elevation [deg]')
    axes[0].set_title('Hypersonic Vehicle Flyover — Multi-Face Tracking')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Active face vs time
    colors = ['#2d6a4f', '#1b4d6e', '#6c5b1e', '#6c2e2e']
    for i in range(4):
        mask = np.array(active_faces) == i
        axes[1].scatter(times[mask], np.array(active_faces)[mask], 
                       c=colors[i], label=f'Face {i+1}', s=20)
    axes[1].set_ylabel('Active Face')
    axes[1].set_xlabel('Time [s]')
    axes[1].set_yticks([0, 1, 2, 3])
    axes[1].set_yticklabels(['Face 1\n(+X)', 'Face 2\n(-X)', 'Face 3\n(+Y)', 'Face 4\n(-Y)'])
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('multiface_tracking_demo.png', dpi=150)
    print("\n  Saved: multiface_tracking_demo.png")
    
    # Coverage plot
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw=dict(projection='polar'))
    
    # Draw coverage wedges for each face
    for i, face in enumerate(mf_opa.faces):
        cfg = face['config']
        theta = np.radians(cfg.normal_azimuth)
        width = np.radians(cfg.max_azimuth_scan * 2)
        
        ax.bar(theta, 90, width=width, bottom=0, 
               color=colors[i], alpha=0.3, label=f'Face {i+1}')
    
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 90)
    ax.set_title('Multi-Face OPA Coverage (Elevation vs Azimuth)', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.tight_layout()
    plt.savefig('multiface_coverage.png', dpi=150)
    print("  Saved: multiface_coverage.png")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_multiface_tracking()
