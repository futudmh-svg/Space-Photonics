"""
VLEO-to-Hypersonic Link Budget Calculator

Usage:
    python vleo_triangulation.py --altitude 300 --velocity 1700 --wavelength 1550e-9

References:
    - Space Photonics Knowledge Base: SPACE_PHOTONICS.md
    - ITU-R P.1621 for atmospheric attenuation models
"""

import argparse
import math

# Physical constants
C = 299792458  # m/s
H = 6.626e-34  # J·s
K_B = 1.381e-23  # J/K

# Default parameters
DEFAULT_WAVELENGTH = 1550e-9  # m
DEFAULT_TX_POWER = 1.0  # W
DEFAULT_TX_APERTURE = 0.1  # m (10 cm)
DEFAULT_RX_APERTURE = 0.05  # m (5 cm)
DEFAULT_ALTITUDE = 300e3  # m (300 km VLEO)
DEFAULT_VELOCITY = 1700  # m/s (~Mach 5 at 30 km altitude)
DEFAULT_ELEVATION = 30  # degrees


def atmospheric_extinction(elevation_deg: float, wavelength_m: float, aod: float = 0.1) -> float:
    """
    Estimate atmospheric extinction in dB.
    
    Args:
        elevation_deg: Elevation angle above horizon (deg)
        wavelength_m: Wavelength (m)
        aod: Aerosol optical depth at 550 nm (unitless)
    
    Returns:
        Extinction in dB
    """
    # Simplified model: scale AOD by wavelength and air mass
    # air_mass ~ 1/sin(elevation) for elevation > ~10°
    elevation_rad = math.radians(max(elevation_deg, 5.0))
    air_mass = 1.0 / math.sin(elevation_rad)
    
    # Angström exponent ~ 1.3 for typical aerosols
    angstrom = 1.3
    aod_wl = aod * (550e-9 / wavelength_m) ** angstrom
    
    # Convert optical depth to dB: extinction_dB = 10 * log10(exp(tau)) = 4.343 * tau
    tau = aod_wl * air_mass
    extinction_db = 4.343 * tau
    
    return extinction_db


def free_space_path_loss(range_m: float, wavelength_m: float) -> float:
    """
    Calculate free-space path loss in dB.
    
    FSPL = (4πR/λ)²
    """
    fspl_linear = (4 * math.pi * range_m / wavelength_m) ** 2
    fspl_db = 10 * math.log10(fspl_linear)
    return fspl_db


def link_budget(
    tx_power_dbm: float,
    tx_gain_db: float,
    rx_gain_db: float,
    range_m: float,
    wavelength_m: float,
    elevation_deg: float = 30.0,
    aod: float = 0.1,
    pointing_loss_db: float = 3.0,
    system_margin_db: float = 6.0,
) -> dict:
    """
    Calculate VLEO-to-hypersonic optical link budget.
    
    Returns dict with all intermediate values and final SNR estimate.
    """
    fspl_db = free_space_path_loss(range_m, wavelength_m)
    atm_db = atmospheric_extinction(elevation_deg, wavelength_m, aod)
    
    # Total losses
    total_loss_db = fspl_db + atm_db + pointing_loss_db
    
    # Received power
    rx_power_dbm = tx_power_dbm + tx_gain_db + rx_gain_db - total_loss_db
    rx_power_w = 10 ** ((rx_power_dbm - 30) / 10)
    
    # SNR estimation (simplified — assumes shot-noise limited)
    # P_s = received optical power
    # SNR = (R * P_s)² / (2qR(P_s + P_b)B + 4kTB/R_load)
    # For now, return budget breakdown
    
    return {
        "tx_power_dbm": tx_power_dbm,
        "tx_gain_db": tx_gain_db,
        "rx_gain_db": rx_gain_db,
        "range_km": range_m / 1000,
        "wavelength_nm": wavelength_m * 1e9,
        "elevation_deg": elevation_deg,
        "fspl_db": fspl_db,
        "atmospheric_extinction_db": atm_db,
        "pointing_loss_db": pointing_loss_db,
        "total_loss_db": total_loss_db,
        "received_power_dbm": rx_power_dbm,
        "received_power_w": rx_power_w,
        "system_margin_db": system_margin_db,
        "link_margin_db": rx_power_dbm - (-60) - system_margin_db,  # Assuming -60 dBm sensitivity
    }


def aperture_gain(diameter_m: float, wavelength_m: float, efficiency: float = 0.7) -> float:
    """
    Calculate aperture gain in dB.
    
    G = η * (πD/λ)²
    """
    gain_linear = efficiency * (math.pi * diameter_m / wavelength_m) ** 2
    gain_db = 10 * math.log10(gain_linear)
    return gain_db


def main():
    parser = argparse.ArgumentParser(description="VLEO-to-Hypersonic Link Budget Calculator")
    parser.add_argument("--altitude", type=float, default=DEFAULT_ALTITUDE, help="VLEO altitude (m)")
    parser.add_argument("--velocity", type=float, default=DEFAULT_VELOCITY, help="Target velocity (m/s)")
    parser.add_argument("--wavelength", type=float, default=DEFAULT_WAVELENGTH, help="Wavelength (m)")
    parser.add_argument("--tx-power", type=float, default=DEFAULT_TX_POWER, help="TX power (W)")
    parser.add_argument("--tx-aperture", type=float, default=DEFAULT_TX_APERTURE, help="TX aperture (m)")
    parser.add_argument("--rx-aperture", type=float, default=DEFAULT_RX_APERTURE, help="RX aperture (m)")
    parser.add_argument("--elevation", type=float, default=DEFAULT_ELEVATION, help="Elevation angle (deg)")
    
    args = parser.parse_args()
    
    # Calculate gains
    tx_gain = aperture_gain(args.tx_aperture, args.wavelength)
    rx_gain = aperture_gain(args.rx_aperture, args.wavelength)
    
    # Assume slant range (simplified — needs proper geometry)
    # For a VLEO sat at altitude H and target at altitude h_t:
    # Slant range ~ H / sin(elevation) for h_t << H
    slant_range = args.altitude / math.sin(math.radians(args.elevation))
    
    tx_power_dbm = 10 * math.log10(args.tx_power * 1000)  # W to dBm
    
    result = link_budget(
        tx_power_dbm=tx_power_dbm,
        tx_gain_db=tx_gain,
        rx_gain_db=rx_gain,
        range_m=slant_range,
        wavelength_m=args.wavelength,
        elevation_deg=args.elevation,
    )
    
    print("=" * 60)
    print("VLEO-to-Hypersonic Optical Link Budget")
    print("=" * 60)
    for key, val in result.items():
        if isinstance(val, float):
            print(f"  {key:30s}: {val:10.3f}")
        else:
            print(f"  {key:30s}: {val}")
    print("=" * 60)


if __name__ == "__main__":
    main()
