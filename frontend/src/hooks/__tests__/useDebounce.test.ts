import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDebounce } from '../useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 300));
    expect(result.current).toBe('initial');
  });

  it('should debounce value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 300 }
      }
    );

    expect(result.current).toBe('initial');

    // Update value
    rerender({ value: 'updated', delay: 300 });

    // Value should not change immediately
    expect(result.current).toBe('initial');

    // Fast-forward time by 300ms
    vi.advanceTimersByTime(300);

    // Wait for the debounced value to update
    await waitFor(() => {
      expect(result.current).toBe('updated');
    });
  });

  it('should cancel previous timeout on rapid changes', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      {
        initialProps: { value: 'initial' }
      }
    );

    // Rapid changes
    rerender({ value: 'change1' });
    vi.advanceTimersByTime(100);
    
    rerender({ value: 'change2' });
    vi.advanceTimersByTime(100);
    
    rerender({ value: 'change3' });
    vi.advanceTimersByTime(100);

    // Should still be initial
    expect(result.current).toBe('initial');

    // Complete the debounce delay
    vi.advanceTimersByTime(200);

    await waitFor(() => {
      expect(result.current).toBe('change3');
    });
  });

  it('should work with different delay values', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 }
      }
    );

    rerender({ value: 'updated', delay: 500 });

    vi.advanceTimersByTime(300);
    expect(result.current).toBe('initial');

    vi.advanceTimersByTime(200);

    await waitFor(() => {
      expect(result.current).toBe('updated');
    });
  });

  it('should work with non-string values', async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      {
        initialProps: { value: 123 }
      }
    );

    expect(result.current).toBe(123);

    rerender({ value: 456 });
    vi.advanceTimersByTime(300);

    await waitFor(() => {
      expect(result.current).toBe(456);
    });
  });

  it('should work with object values', async () => {
    const obj1 = { name: 'test1' };
    const obj2 = { name: 'test2' };

    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      {
        initialProps: { value: obj1 }
      }
    );

    expect(result.current).toBe(obj1);

    rerender({ value: obj2 });
    vi.advanceTimersByTime(300);

    await waitFor(() => {
      expect(result.current).toBe(obj2);
    });
  });
});
