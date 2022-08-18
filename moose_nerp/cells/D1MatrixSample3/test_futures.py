from concurrent.futures import ProcessPoolExecutor

def testwait(wait):
    import time
    print('sleeping {} seconds'.format(wait))
    time.sleep(wait)

with ProcessPoolExecutor() as executor:
    jobs = range(5,30)
    results = [executor.submit(testwait,j) for j in jobs]
