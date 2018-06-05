from threading import Timer

class LoopTimer(Timer):
    def run(self):
        while True:  
            self.finished.wait(self.interval)  
            if self.finished.is_set():  
                self.finished.set()  
                break  
            self.function(*self.args, **self.kwargs) 
