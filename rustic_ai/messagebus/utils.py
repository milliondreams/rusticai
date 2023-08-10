import time
from datetime import datetime, timezone
from enum import IntEnum

# Define the date
date = datetime(2023, 1, 1, tzinfo=timezone.utc)
# Get the millisecond timestamp
EPOCH = int(date.timestamp() * 1000)

# Constants for magic numbers
MACHINE_ID_BITMASK = 0xFF  # Allows for 256 unique machine IDs using 8 bits
SEQUENCE_BITMASK = 0xFFF  # 12 bits, allows for 4096 unique sequence numbers
PRIORITY_BITMASK = 0x7  # 3 bits, allows for 8 unique priority levels
PRIORITY_SHIFT: int = 61
TIMESTAMP_SHIFT: int = 22
MACHINE_ID_SHIFT: int = 12


class ClockMovedBackwardsError(Exception):
    pass


class Priority(IntEnum):
    """
    Priority levels for messages.
    """

    LOWEST = 7
    VERY_LOW = 6
    LOW = 5
    NORMAL = 4
    ABOVE_NORMAL = 3
    HIGH = 2
    IMPORTANT = 1
    URGENT = 0


class GemstoneID:
    def __init__(self, priority: Priority, timestamp: int, machine_id: int, sequence_number: int):
        self.priority: int = priority.value
        self.timestamp = timestamp
        self.machine_id = machine_id
        self.sequence_number = sequence_number

    def to_int(self):
        p = (self.priority & PRIORITY_BITMASK) << PRIORITY_SHIFT
        t = (self.timestamp - EPOCH) << TIMESTAMP_SHIFT
        m = (self.machine_id & MACHINE_ID_BITMASK) << MACHINE_ID_SHIFT
        s = self.sequence_number & SEQUENCE_BITMASK

        return p | t | m | s

    @classmethod
    def from_int(cls, id):
        priority = (id >> PRIORITY_SHIFT) & PRIORITY_BITMASK
        timestamp = ((id >> TIMESTAMP_SHIFT) & ((1 << (PRIORITY_SHIFT - TIMESTAMP_SHIFT)) - 1)) + EPOCH
        machine_id = (id >> MACHINE_ID_SHIFT) & ((1 << (TIMESTAMP_SHIFT - MACHINE_ID_SHIFT)) - 1)
        sequence_number = id & SEQUENCE_BITMASK

        return cls(Priority(priority), timestamp, machine_id, sequence_number)

    def __lt__(self, other):
        if not isinstance(other, GemstoneID):
            raise TypeError(f"Cannot compare GemstoneID to {type(other)}")
        return (self.priority, self.timestamp, self.machine_id, self.sequence_number) < (
            other.priority,
            other.timestamp,
            other.machine_id,
            other.sequence_number,
        )

    def __eq__(self, other):
        if not isinstance(other, GemstoneID):
            raise TypeError(f"Cannot compare GemstoneID to {type(other)}")
        return (self.priority, self.timestamp, self.machine_id, self.sequence_number) == (
            other.priority,
            other.timestamp,
            other.machine_id,
            other.sequence_number,
        )

    def to_string(self) -> str:
        return self.__dict__.__str__()  # pragma: no cover


class GemstoneGenerator:
    def __init__(self, machine_id: int):
        self.machine_id = machine_id
        self.sequence_number = 0
        self.last_timestamp = -1

    def get_id(self, priority: Priority) -> GemstoneID:
        """
        Generate a new snowflake ID additionally considering the given priority.

        :param priority: The priority of the ID (between 0 and 7, inclusive)
        :return: The generated ID
        """

        timestamp = time.time_ns() // 1000000
        if timestamp < self.last_timestamp:  # TBD: Write test case for this # pragma: no cover
            raise ClockMovedBackwardsError("Clock moved backwards!")

        if timestamp == self.last_timestamp:
            self.sequence_number = (self.sequence_number + 1) & SEQUENCE_BITMASK
            if self.sequence_number == 0:  # TBD: Write test case
                # We have already generated 4096 IDs in this millisecond, wait until the next one
                while timestamp <= self.last_timestamp:  # pragma: no cover
                    timestamp = time.time_ns() // 1000000
        else:
            self.sequence_number = 0

        self.last_timestamp = timestamp

        return GemstoneID(priority, timestamp, self.machine_id, self.sequence_number)
