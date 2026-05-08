-- Run this entire file in the Supabase SQL Editor
-- (Dashboard → SQL Editor → New query → paste → Run)

CREATE TABLE employees (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE time_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    clock_in TIMESTAMPTZ NOT NULL,
    clock_out TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT clock_out_after_clock_in CHECK (clock_out IS NULL OR clock_out > clock_in)
);

CREATE INDEX idx_time_entries_employee ON time_entries(employee_id);
CREATE INDEX idx_time_entries_clock_in ON time_entries(clock_in);
