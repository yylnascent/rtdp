class RTDPCriticalError(Exception):
    """RTDP struggle in a critical error."""

class RTDPConfigurationError(RTDPCriticalError):
    """Invalid configuration error."""