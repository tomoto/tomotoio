from bluepy.btle import UUID


class UUIDs:
    """UUIDs defined for the services and characteristics for Toio."""

    # Service UUID
    SERVICE = UUID("10B20100-5B3B-4571-9508-CF3EFCD7BBAE")

    # Characteristic UUIDs
    TOIO_ID = UUID("10B20101-5B3B-4571-9508-CF3EFCD7BBAE")
    MOTOR = UUID("10B20102-5B3B-4571-9508-CF3EFCD7BBAE")
    LIGHT = UUID("10B20103-5B3B-4571-9508-CF3EFCD7BBAE")
    SOUND = UUID("10B20104-5B3B-4571-9508-CF3EFCD7BBAE")
    MOTION = UUID("10B20106-5B3B-4571-9508-CF3EFCD7BBAE")
    BUTTON = UUID("10B20107-5B3B-4571-9508-CF3EFCD7BBAE")
    BATTERY = UUID("10B20108-5B3B-4571-9508-CF3EFCD7BBAE")
    CONFIG = UUID("10B201FF-5B3B-4571-9508-CF3EFCD7BBAE")


class Handles:
    """Characteristic handles defined for Toio."""

    # Note we assume these values are static and never change.
    TOIO_ID = 0x000d
    MOTOR = 0x0011
    LIGHT = 0x0014
    SOUND = 0x0017
    MOTION = 0x001a
    BUTTON = 0x001e
    BATTERY = 0x0022
    CONFIG = 0x0026
