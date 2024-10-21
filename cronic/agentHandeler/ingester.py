from celery import Celery
app = Celery('release', broker='redis://:dctestpass@3.142.123.195:6379/0')

@app.task(name='tasks.release')
def release(results, agentId, userId):
    print(results)
    pass

def main():
    pass

if __name__ == "__main__":
    main()
