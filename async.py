import threading, time
class AsyncWrite(threading.Thread):
    def __init__(self,text,outf):
        threading.Thread.__init__(self)
        self.text = text
        self.outf = outf
    def run(self):
        f = open(self.outf,"a")
        f.write(self.text + "\n")
        f.close()
        time.sleep(2)
        print "finished background write to: "+str(self.outf)
        
def Main():
    mes = raw_input("enter message.\n")
    bg = AsyncWrite(mes, 'outfile.txt')
    bg.start()
    print "Main:program continues...."
    print "MAIN"+ str(100+400)
    bg.join()
    print "MAIN:thread finished."
    
if __name__ == '__main__':
    Main()
