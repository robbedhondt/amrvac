import numpy as np

pg_table = np.asarray([0.01, 0.02, 0.05, 0.10, 0.20])           # dyn cm-2
T_table  = np.asarray([6000., 8000., 10000., 12000., 14000.])   # Kelvin
alt_table = np.asarray([10000, 20000, 30000])                   # km

ionisation_10k = np.asarray([[0.74, 0.62, 0.44, 0.31, 0.20],
                             [0.83, 0.72, 0.55, 0.44, 0.35],
                             [0.87, 0.79, 0.70, 0.69, 0.73],
                             [0.91, 0.85, 0.82, 0.85, 0.89],
                             [0.93, 0.89, 0.89, 0.92, 0.94]])

f_10k = np.asarray([[5.0, 4.6, 4.2, 4.0, 4.0],
                    [6.7, 5.8, 5.0, 4.8, 4.7],
                    [8.1, 6.8, 5.3, 5.1, 5.3],
                    [9.1, 7.0, 5.0, 4.9, 5.2],
                    [9.8, 7.1, 4.9, 4.8, 5.0]])

# 20 000 km altitude table
ionisation_20k = np.asarray([[0.73, 0.60, 0.41, 0.29, 0.18],
                             [0.81, 0.70, 0.52, 0.41, 0.33],
                             [0.86, 0.78, 0.68, 0.68, 0.72],
                             [0.90, 0.84, 0.81, 0.84, 0.88],
                             [0.92, 0.88, 0.89, 0.91, 0.94]])

f_20k = np.asarray([[4.7, 4.2, 3.8, 3.7, 3.6],
                    [6.3, 5.4, 4.6, 4.4, 4.3],
                    [7.6, 6.3, 4.8, 4.7, 4.9],
                    [8.6, 6.5, 4.6, 4.5, 4.8],
                    [9.2, 6.4, 4.5, 4.4, 4.6]])

# 30 000 km altitude
ionisation_30k = np.asarray([[0.71, 0.58, 0.39, 0.27, 0.17],
                             [0.80, 0.68, 0.50, 0.39, 0.32],
                             [0.85, 0.76, 0.66, 0.67, 0.71],
                             [0.89, 0.83, 0.81, 0.84, 0.88],
                             [0.92, 0.88, 0.88, 0.91, 0.93]])

f_30k = np.asarray([[4.5, 4.0, 3.5, 3.4, 3.4],
                    [6.1, 5.1, 4.3, 4.0, 4.0],
                    [7.4, 6.0, 4.5, 4.3, 4.5],
                    [8.3, 6.1, 4.2, 4.2, 4.5],
                    [8.9, 6.0, 4.2, 4.1, 4.3]])

def get_ionisation_table(altitude=20000):
    if altitude == 10000:
        itable = ionisation_10k
        ftable = f_10k
    elif altitude == 20000:
        itable = ionisation_20k
        ftable = f_20k
    elif altitude == 30000:
        itable = ionisation_30k
        ftable = f_30k
    else:
        raise ValueError("altitude not specified correctly. Use 10000, 20000 or 30000 (integers)")

    return itable, ftable