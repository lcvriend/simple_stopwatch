Simple stopwatch.

## Attributes
### Templates
- `START` (Template|None): Message to show at stopwatch start.
- `LAP` (Template|None): Message to show when lap().
- `SPLIT` (Template|None): Message to show when split().
- `STOP` (Template|None): Message to show when stop().

### Stopwatch internals
- `running` (bool): If stopwatch is currently running.
- `times` (list[floats]): Stored times.
- `timestamp` (datetime): Current timestamp.
- `laps` (list[float]): Lap durations in seconds.
- `splits` (list[float]): Lap durations compared to stopwatch start time.
- `current_time` (int): Current lap.

## Methods
### Stopwatch metchanics
- `click()` -> None: Store current time to times if stopwatch is running.
- `start()` -> None: Start stopwatch and click().
- `lap()` -> float|None: Show lap duration, click(), return duration.
- `split()` -> float|None: Show current run time and return duration.
- `stop()` -> float|None: Stop stopwatch and click().
- `reset()` -> None: Stop stopwatch and empty stored times.

### Formatters
- `format_seconds(duration)` -> str: "241s"
- `format_timedelta(duration)` -> str: "5 days, 4:50:34.523000"
- `format_min_sec_ms(duration)` -> str: "09:59.981"

### Decorators
- `time_function(callable)` -> callable: Function that displays run time.