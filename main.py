import multiprocessing
import server
import backend

if __name__ == "__main__":
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=backend.start,args=(queue,)) # start data collection
    process.start()
    server.start(queue) # start viewing server