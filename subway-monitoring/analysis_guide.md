# Subway Data Analysis Guide

This document outlines potential data analysis projects using the `realtime_train_positions` table.

## Table Schema
See `database/schema.sql` for full details. Key columns:
- `subway_id`: Line ID
- `station_id`: Current Station
- `train_number`: Unique Train No
- `reception_time`: Timestamp of position update
- `train_status`: 0:Entry, 1:Arrived, 2:Departed...
- `is_express`: Express train flag

## Analysis Projects

### 1. Real-time Interval Regularity Monitoring
**Goal:** Detect "bunching" or gaps in service.
**Query Logic:**
1.  Group by `subway_id`, `station_id`.
2.  Order by `reception_time`.
3.  Calculate `delta_t` between consecutive trains arriving (`train_status` = '1').
4.  Monitor if `delta_t` exceeds threshold (e.g., > 10 min for Line 1).

### 2. Section Travel Time Analysis
**Goal:** Identify slow track sections.
**Query Logic:**
1.  Select a specific `train_number`.
2.  Find time `t1` when `train_status`='2' (Departed) at Station A.
3.  Find time `t2` when `train_status`='1' (Arrived) at Customer Station B (Next Station).
4.  Travel Time = `t2 - t1`.
5.  Aggregate average travel time for (Station A -> Station B) pair.

### 3. Last Train Verification
**Goal:** Ensure last train completes route.
**Query Logic:**
1.  Select * where `is_last_train` = TRUE.
2.  Check if `destination_station_id` matches the final recorded station in the night.

### 4. Express Train Efficiency
**Goal:** Quantify time savings of Express vs Local.
**Query Logic:**
1.  Calculate total trip time for `is_express`=TRUE trains between two major hubs (e.g., A to B).
2.  Compare with average trip time for `is_express`=FALSE trains.
