RosterSync — Network Service Scheduling System
Overview

RosterSync is a simulation-based system that demonstrates important concepts from:

Design and Analysis of Algorithms (DAA)
Operating Systems (OS)

The project focuses on:

Network Service Boot Sequencing using Topological Sort
Bandwidth Job Scheduling using Preemptive Priority Scheduling
Starvation Prevention using Aging

The system is implemented as an interactive web application using Streamlit
Features
1. Network Service Boot Sequencer
Accepts service dependencies
Generates valid startup order
Uses DFS-based Topological Sort
Detects circular dependencies
Displays dependency execution order

2. Preemptive Priority Scheduler
Simulates bandwidth-heavy network jobs
Uses priority-based scheduling
Supports process arrival time
Generates execution/context-switch logs
Calculates waiting times
Example Jobs
Backup Process
Streaming Service
Emergency Alert
OS Update
3. Aging-Based Starvation Prevention
Demonstrates starvation of low-priority jobs
Implements priority aging
Gradually improves waiting process priority
Compares:
Without Aging
With Aging
