import cProfile
import hiq

with cProfile.Profile() as pr:
    hiq.mod("main").main()
    pr.dump_stats("result.pstat")
