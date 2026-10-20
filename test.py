from etee import Ahrs, EteeController, Quaternion

# Test update_relative (6-axis: gyro + accel only)
ahrs_relative = Ahrs()
gyro = [0.01, 0.02, 0.01]
accel = [0.1, 0.05, 1.0]   # Slightly off-axis to avoid degenerate zero-step case

q1 = ahrs_relative.get_quaternion(gyro, accel)
q2 = ahrs_relative.get_quaternion(gyro, accel)

print("--- update_relative (6-axis) ---")
print("q1:", list(q1))
print("q2:", list(q2))
assert not any(str(v) == 'nan' for v in q1), "update_relative produced NaN"

# Test update_absolute (9-axis: gyro + accel + mag)
ahrs_absolute = Ahrs()
mag = [0.3, 0.1, 0.9]

q3 = ahrs_absolute.get_quaternion(gyro, accel, mag)
q4 = ahrs_absolute.get_quaternion(gyro, accel, mag)

print("\n--- update_absolute (9-axis) ---")
print("q3:", list(q3))
print("q4:", list(q4))
assert not any(str(v) == 'nan' for v in q3), "update_absolute produced NaN"

print("\nAll tests passed.")