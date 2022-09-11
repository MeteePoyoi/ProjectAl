## Formatter Fields

See https://docs.python.org/3/library/logging.html#formatter-objects

#### %(asctime)s

-   Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time).

#### %(created)f

-   Time when the LogRecord was created (as returned by time.time()).

#### %(filename)s

-   Filename portion of pathname.

#### %(funcName)s

-   Name of function containing the logging call.

#### %(levelname)s

-   Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').

#### %(levelno)s

-   Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).

#### %(lineno)d

-   Source line number where the logging call was issued (if available).

#### %(message)s

-   The logged message, computed as msg % args. This is set when Formatter.format() is invoked.

#### %(module)s

-   Module (name portion of filename).

#### %(msecs)d

-   Millisecond portion of the time when the LogRecord was created.

#### %(name)s

-   Name of the logger used to log the call.

#### %(pathname)s

-   Full pathname of the source file where the logging call was issued (if available).

#### %(process)d

-   Process ID (if available).

#### %(processName)s

-   Process name (if available).

#### %(relativeCreated)d

-   Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.

#### %(thread)d

-   Thread ID (if available).

#### %(threadName)s

-   Thread name (if available).

### Field Width

Use formst %(field)-NNd or $(field)-NNs, for example

```
%(name)-10s
```
