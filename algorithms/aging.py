class Job:

    def __init__(self, name, arrival, burst, priority):

        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.priority = priority
        self.waiting = 0


def run_scheduler_with_aging(jobs_data):

    jobs = []

    for job in jobs_data:

        jobs.append(
            Job(
                job["name"],
                job["arrival"],
                job["burst"],
                job["priority"]
            )
        )

    time = 0
    completed = 0
    n = len(jobs)

    log = []

    while completed < n:

        available = [

            job for job in jobs

            if job.arrival <= time and job.remaining > 0
        ]

        if not available:
            time += 1
            continue

        # Higher priority = lower number
        current = min(available, key=lambda x: x.priority)

        log.append(
            f"Time {time}: Running {current.name} "
            f"(Priority {current.priority})"
        )

        current.remaining -= 1

        for job in available:

            if job != current:

                job.waiting += 1

                # Aging logic
                if job.waiting % 5 == 0 and job.priority > 1:

                    job.priority -= 1

                    log.append(
                        f"Aging Applied to {job.name}. "
                        f"New Priority: {job.priority}"
                    )

        if current.remaining == 0:

            completed += 1

            log.append(
                f"{current.name} completed at time {time + 1}"
            )

        time += 1

    waiting_times = {

        job.name: job.waiting

        for job in jobs
    }

    return log, waiting_times