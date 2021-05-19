import sqlite3
import sys

argv = sys.argv
cohort_id = sys.argv[1]
pid = sys.argv[2]

conn = sqlite3.connect('../db.sqlite3')
c = conn.cursor()
c.execute('UPDATE app_cohortmodel SET pid = ? WHERE ID = ?;', (pid, cohort_id))
conn.commit()
conn.close()