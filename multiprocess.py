import multiprocessing
from concurrent import futures

_processes = multiprocessing.cpu_count()

def multiprocess(func, iter_args,processes=_processes):
    with futures.ProcessPoolExecutor(max_workers=processes) as ex:
        try:
            results = ex.map(func, iter_args)
        except futures.process.BrokenProcessPool as e:
            print('could not start new tasks: {}'.format(e))
        else:
            return results


def thread(func, iter_args,processes=_processes*2):
    with futures.ThreadPoolExecutor(max_workers=processes) as ex:
        results = ex.map(func, iter_args)
        return results



"""
from multiprocessing.dummy import Pool as ThreadPool

def multi(func, iter_args,processes=_processes):
    pool = multiprocessing.Pool(processes)
    results = pool.map(func, iter_args)
    pool.close()
    pool.join()
    return results

def thread(func, iter_args,processes=_processes*2):
    pool = ThreadPool(processes)
    results = pool.map(func, iter_args)
    pool.close()
    pool.join()
    return results
"""

