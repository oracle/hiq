from hiq.hiq_utils import get_global_hiq_status, set_global_hiq_status

if __name__ == "__main__":
    set_global_hiq_status(True)
    b = get_global_hiq_status()
    print(b)

    set_global_hiq_status(False)
    b = get_global_hiq_status()
    print(b)
