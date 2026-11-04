Price Extractor

A portfolio project for concurrent price extraction across multiple sites, using a per-domain task queue and asynchronous SQL persistence.

How it works

Extraction runs concurrently across sites, so a slow or unresponsive site doesn't hold up the others.Each domain gets its own queue, which isolates rate limiting and blocking behavior per site instead of letting one bad domain affect the rest. A selector cache stores the already discovered selector for each site, avoiding redetection on every repeated extraction. Writes to the database are asynchronous, since multiple workers can be writing at the same time and non-blocking access is needed to avoid data corruption and wasted time waiting on I/O.

Stack

Python (asyncio), aiosqlite, ...

Running it ...

#Out of scope

This project is a portfolio piece focused on concurrency, task queuing, and asynchronous persistence. Anti-bot bypass logic is not part of this implementation.
