import textwrap
from datetime import datetime, timedelta
from functools import wraps
from string import Template
from time import perf_counter
from types import FunctionType
from typing import Callable, Literal


type DurationFormatterOptions = Literal['seconds', 'timedelta', 'min_sec_ms']
type DurationFormatter = DurationFormatterOptions|Callable[[float], str]


class Stopwatch:
    """
    Simple stopwatch.

    Attributes:
    Templates
    - START (Template|None): Message to show at stopwatch start.
    - LAP (Template|None): Message to show when lap().
    - SPLIT (Template|None): Message to show when split().
    - STOP (Template|None): Message to show when stop().

    Stopwatch internals
    - running (bool): If stopwatch is currently running.
    - times (list[floats]): Stored times.
    - timestamp (datetime): Current timestamp.
    - laps (list[float]): Lap durations in seconds.
    - splits (list[float]): Lap durations compared to stopwatch start time.
    - current_time (int): Current lap.

    Methods:
    Stopwatch metchanics
    - click() -> None: Store current time to times if stopwatch is running.
    - start() -> None: Start stopwatch and click().
    - lap() -> float|None: Show lap duration, click(), return duration.
    - split() -> float|None: Show current run time and return duration.
    - stop() -> float|None: Stop stopwatch and click().
    - reset() -> None: Stop stopwatch and empty stored times.

    Formatters
    - format_seconds(duration) -> str: "241s"
    - format_timedelta(duration) -> str: "5 days, 4:50:34.523000"
    - format_min_sec_ms(duration) -> str: "09:59.981"

    Decorators
    - time_function(callable) -> callable: Function that displays run time.
    """
    # templates
    START: Template|None = Template("""
+==================================================================+
    :: STOPWATCH :: ${name}

    started recording at: ${timestamp}
+------------------------------------------------------------------+
""")
    LAP: Template|None = Template("[lap ${lap} finished in ${duration}]")
    SPLIT: Template|None = Template("[current run time is ${duration}]")
    STOP: Template|None = Template("""
+------------------------------------------------------------------+
    stopped recording at: ${timestamp}

    :: TOTAL RUN TIME :: ${duration}
+==================================================================+
""")

    def __init__(
        self,
        name: str|None = None,
        duration_formatter: DurationFormatter = 'seconds'
    ) -> None:
        self.name = '' if name is None else name
        self.times: list[float] = []
        self.running: bool = False

        match duration_formatter:
            case 'seconds':
                self.duration_formatter = self.format_seconds
            case 'timedelta':
                self.duration_formatter = self.format_timedelta
            case 'min_sec_ms':
                self.duration_formatter = self.format_min_sec_ms
            case FunctionType():
                self.duration_formatter = duration_formatter

    def click(self) -> None:
        "Store current time to times if stopwatch is running."
        if not self.running:
            return None
        now = perf_counter()
        self.times.append(now)

    def start(self, end=None, **kwargs) -> None:
        "Start stopwatch and store current time to times."
        self.running = True
        self.click()
        if self.START is not None:
            msg = self.START.substitute(
                name = self.name,
                timestamp = self.timestamp,
                **kwargs
            )
            print(msg, end=end)

    def lap(self, end=None, **kwargs) -> float|None:
        "Show lap and store current time to times."
        if not self.running:
            return None
        self.click()
        duration = self.times[-1] - self.times[-2]
        if self.LAP is not None:
            msg = self.LAP.substitute(
                name = self.name,
                timestamp = self.timestamp,
                lap = self.current_lap,
                duration = self.duration_formatter(duration),
                **kwargs
            )
            print(msg, end=end)
        return duration

    def split(self, end=None, **kwargs) -> float|None:
        "Show current runtime, do not store current time to times."
        if not self.running:
            return None
        now = perf_counter()
        duration = now - self.times[0]
        if self.SPLIT is not None:
            msg = self.SPLIT.substitute(
                name = self.name,
                timestamp = self.timestamp,
                duration = self.duration_formatter(duration),
                **kwargs
            )
            print(msg, end=end)
        return duration

    def stop(self, end=None, **kwargs) -> float|None:
        "Stop recording and store current time to times."
        if not self.running:
            return None
        self.click()
        self.running = False
        duration = self.times[-1] - self.times[0]
        if self.STOP is not None:
            msg = self.STOP.substitute(
                name = self.name,
                timestamp = self.timestamp,
                duration= self.duration_formatter(duration),
                **kwargs
            )
            print(msg, end=end)
        return duration

    def reset(self) -> None:
        "Stop recording and reset times."
        self.running = False
        self.times = []

    #formatters
    @staticmethod
    def format_seconds(duration: float) -> str:
        return f"{duration:.2f}s"

    @staticmethod
    def format_timedelta(duration: float) -> str:
        return str(timedelta(seconds=duration))

    @staticmethod
    def format_min_sec_ms(seconds: float) -> str:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{minutes:02d}:{remaining_seconds:02d}.{milliseconds:02d}"

    # internals
    @property
    def timestamp(self) -> datetime:
        "Current timestamp."
        return datetime.now()

    @property
    def laps(self) -> list[float]:
        "Lap durations in seconds."
        return [t2 - t1 for t1, t2 in zip(self.times, self.times[1:])]

    @property
    def splits(self) -> list[float]:
        "Lap durations in seconds compared to stopwatch start time."
        return [t - self.times[0] for t in self.times]

    @property
    def current_lap(self) -> int:
        "Current lap."
        return len(self.times) - 1

    # decorator
    @classmethod
    def time_function(cls, line_width=80):
        def decorator(func, *args, **kwargs):
            START = Template("${func_name}${params}")
            STOP = Template("${duration}")
            @wraps(func)
            def wrapper(*args, **kwargs):
                stopwatch = cls(duration_formatter='min_sec_ms')
                stopwatch.START = START
                stopwatch.STOP = STOP
                func_name = f"[{func.__name__}] "
                kwarg_rep = [f"{k}={v}" for k,v in kwargs.items()]
                params = ', '.join(list(args) + kwarg_rep)
                duration_length = 9
                max_length = line_width - len(func_name) - duration_length
                params_trunc = textwrap.shorten(params, width=max_length)
                params_fill = f"{params_trunc:<{max_length}}"
                stopwatch.start(
                    func_name = func_name,
                    params = params_fill,
                    end=' ',
                )
                result = func(*args, **kwargs)
                stopwatch.stop()
                return result
            return wrapper
        return decorator