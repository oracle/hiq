import cProfile
import hiq
import time

m = hiq.mod("main")
with cProfile.Profile() as pr:
    start = time.monotonic()
    m.main()
    print(time.monotonic() - start)
pr.dump_stats("result_cprofile.pstat")
